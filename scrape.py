import urllib2
from bs4 import BeautifulSoup
import re

def get_house_members():
    member_list_url = "http://www.ilga.gov/house"
    f = urllib2.urlopen( member_list_url)
    s = BeautifulSoup(f, 'html.parser')
    member_name_num_dict={}
    member_num_name_dict={}

    for x in s.find_all(href=re.compile("/house/Rep")):
        num=str(x).split("MemberID=")[1][:4]
        member_name_num_dict[x.string] = num
        member_num_name_dict[num] = x.string

    return member_name_num_dict, member_num_name_dict

name2num, num2name = get_house_members()

print name2num["Kathleen Willis"]

class BillListItem:
    def __init__(self,td_list):
        self.bill_num = td_list[0]
        self.bill_sponsor=td_list[1]
        self.bill_abr_short_desc=td_list[2]
        self.bill_chamber=td_list[3]
        self.bill_last_action=td_list[4]
        self.bill_last_action_date=td_list[5]

    def str_me(self):
        out=[self.str_bill_num(),
             self.bill_sponsor.string,
             self.bill_abr_short_desc.string,
             self.bill_chamber.string,
             self.bill_last_action.string,
             self.bill_last_action_date.string]
        return ";".join(out)

    def str_bill_num(self):
        return self.bill_num.string

    def bill_url(self):
        return self.bill_num.find('a').get('href')
    

def get_timeline( bill):
    url = bill.bill_url()
    f = urllib2.urlopen( 'http://www.ilga.gov' + url)
    s = BeautifulSoup(f, 'html.parser')
    return get_timeline_table(s)

def get_member_bills( id='2237'):
    url="http://www.ilga.gov/house/RepBills.asp?MemberID=" + id
    f = urllib2.urlopen( url)
    s = BeautifulSoup(f, 'html.parser')
    bill_list = []

    for x in s.find_all("tr"):
        y = x.find_all("td")
        if len(y) != 6:
            continue
        bli = BillListItem( y)
        bill_list.append( bli)

    bill_list.pop(0)

    return bill_list


def get_filed_fields(soup):
    s_all_td = soup.find_all("td")
    filed_with_clerk = s_all_td[23]
    date, chamber = [x.string for x in filed_with_clerk.find_all('table')[3].\
                     find_all('td')[-3:-1]]
    filer = filed_with_clerk.find_all('table')[3].find_all('td')[-1].\
            find("a").get_text()
    date = date.encode('ascii',errors='ignore')
    return date, chamber, filer


def get_timeline_table(soup):
    table = []
    s_all_td = soup.find_all('td')
    for i in range(37,len(s_all_td)-6):
        st = s_all_td[i].get_text().encode('ascii',errors='ignore')
        table.append( st)

    dates = [ table[3*i] for i in range( len(table)/3)]
    chamber = [ table[3*i+1] for i in range( len(table)/3)]
    action = [ table[3*i+2] for i in range( len(table)/3)]
    return zip(dates, chamber, action)


if __name__ == "__main__":

    willis_num = name2num["Kathleen Willis"]
    bl = get_member_bills( willis_num)

    timelines = {}
    for b in bl:
        timelines[b.str_bill_num()] = get_timeline( b)

    ## unfortunately get_timeline does not parse all bill timelines
    ## correctly


    

    for tl in ['HB696', 'HB972', 'HB6252']:
        print tl
        for x in timelines[tl][:3]:
            print x
        for x in  timelines[tl][-3:]:
            print x

    

    
    


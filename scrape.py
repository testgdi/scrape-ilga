import urllib2
from bs4 import BeautifulSoup
import re
from dateutil.parser import parse

def is_date(string):
    """
    check if a string is a date, i.e. "1/12/2015"
    """
    try:
        parse(string)
        return True
    except ValueError:
        return False

class BillListItem:
    """
    Hold some properties of a bill
    """
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

def get_house_members():
    """
    get all the hous members, and get their names and ids
    """
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

def get_multi_timeline(soup):
    """
    given a soup for a bills webpage, extract the timeline
    """
    dates = soup.find_all("td", align="right",
                       valign="top", width="13%")
    chamber = soup.find_all("td", align="center",
                       valign="top", width="12%")
    action = soup.find_all("td", align="left",
                       valign="top", width="75%")
    dates = [x.get_text().encode('ascii',errors='ignore') for x in dates]
    chamber = [x.get_text().encode('ascii',errors='ignore') for x in chamber]
    action = [x.get_text().encode('ascii',errors='ignore') for x in action]

    table = zip( dates, chamber, action)
    return table

def get_timeline( bill):
    """
    given a bill object, extract the timeline
    """
    url = bill.bill_url()
    f = urllib2.urlopen( 'http://www.ilga.gov' + url +"#actions")
    s = BeautifulSoup(f, 'html.parser')
    return get_multi_timeline(s)

def get_member_bills( id='2237'):
    """
    given a member id, get all the bills they sponsor or co-sponsor
    """
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

if __name__ == "__main__":

    name2num, num2name = get_house_members()

    willis_num = name2num["Kathleen Willis"]
    print willis_num

    bl = get_member_bills( willis_num)

    timelines = {}
    for b in bl:
        timelines[b.str_bill_num()] = get_timeline( b)

    for tl in timelines:
        print tl
        for x in timelines[tl][:3]:
            print x
        for x in  timelines[tl][-3:]:
            print x

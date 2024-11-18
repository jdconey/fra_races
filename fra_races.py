# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 17:13:31 2022

@author: jdconey
"""

import requests
import bs4
from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight
from pytz import timezone, country_timezones
from datetime import datetime, timedelta

def standard_replace(s:str) -> str:
    """
    Removes double spaces, new lines, 'li' and 'strong' tags from the given string
    """
    s = s.replace("  ","")
    s = s.replace('\n','')
    s = s.replace("<li>","")
    s = s.replace("</li>","")
    s = s.replace("<strong>","")
    s = s.replace("</strong>","")
    return s


def remove_td(s:str) -> str:
    """removes 'td' tags from the string"""
    s = str(s) if not isinstance(s,str) else s
    s = s.replace("<td>","")
    s = s.replace("</td>","")
    return s


def get_races_from_page(soup):
    races = soup.find_all('tr')
    race_dict={}
    for race in races:
        try:
            details = race.find_all('td')
            if not details:
                continue
            name_link = str(details[1]).replace('<td class="titleCol"><a href="','')
            name_link = name_link.split('">')
            race_dict[name_link[0]] = {
                'date':remove_td(details[0]),
                'name':name_link[1].replace("</a></td>",''),
                'cat':remove_td(details[2]),
                'country':remove_td(details[3]),
                'region':remove_td(details[4]),
                'link':'https://races.fellrunner.org.uk'+name_link[0]
            }
        except Exception as e:
            print('error',e)
    return race_dict

def extract_event_info(url):
    pg = requests.get(url)
    soup = bs4.BeautifulSoup(pg.content,'html.parser')
    event_info = [str(i) for i in soup.find_all("li")]

    full_str=''
    extra_info=[]
    for k in event_info:
        full_str= full_str + k

        if "Date &amp; time" in k:
            dt = k.replace("Date &amp; time:",'')
            dt = standard_replace(dt)
            extra_info.append("Date & time: " + dt)
        elif "Start time info" in k:
            if "Date &amp; time" not in full_str:
                for k2 in event_info:
                    if 'Date' in k2:
                        dt2 = k2.replace("Date:", '')
                        dt2 = standard_replace(dt2)
                dt = k.replace("Start time info:", '')
                dt = standard_replace(dt)
                dt = dt.replace('.', ':')
                dt = dt2 + ' at ' + dt
                extra_info.append("Date & time: " + dt)
        elif "Date:" in k:
            if  "Date &amp; time" not in full_str:
                if "Start time info" not in full_str:
                    dt = k.replace("Date:", '')
                    dt = standard_replace(dt)
                    dt = dt.replace(".", ":")
                    dt = dt + " at 00:00"
        if "Venue:" in k:
            venue = k.replace("Venue:","")
            venue = standard_replace(venue)
            venue = venue.replace(":", "\:")
            #  venue = venue.encode()
#        if "Distance:" in k or "Climb:" in k or "Venue:" in k or "Grid reference:" in k or "Skills:" in k or "Minimum age:" in k  or "Entry:" in k:
        if "Distance:" in k or "Climb:" in k or "Grid reference:" in k or "Entry" in k or "entry" in k:
            info = standard_replace(k)
            extra_info.append(info)
    # print(url)
    return dt, venue, extra_info



def make_cal(race_dict):
    cal = Calendar()
    cal['prodid'] = '-//Mozilla.org/NONSGML Mozilla Calendar V1.1//EN'
    cal['version'] = '2.0'
    cal['method'] = 'REQUEST'

    tzc = Timezone({
    'tzid': 'Europe/London',
    'x-lic-location': 'Europe/London',
    })

    tzs = TimezoneStandard({
        "tzname":"GMT",
        "TZOFFSETFROM":timedelta(hours=1),
        "TZOFFSETTO":timedelta(hours=0),
        "dtstart":datetime(1970, 10, 25, 2, 0, 0),
        "rrule":{'freq': 'yearly', 'bymonth': 10, 'byday': '-1su', 'interval': '1'}
    })
    tzd = TimezoneDaylight({
        "tzname":'BST',
        "dtstart":datetime(1970, 3, 29, 1, 0, 0),
        "rrule":{'freq': 'yearly', 'bymonth': 3, 'byday': '-1su', 'interval': '1'},
        "TZOFFSETFROM":timedelta(hours=0),
        "TZOFFSETTO":timedelta(hours=1),
    })
    tzc.add_component(tzs)
    tzc.add_component(tzd)
    cal.add_component(tzc)

    for i, entry in enumerate(race_dict):

        info = race_dict[entry]
        #   print(info['link'])
        dt, venue, extra_info = extract_event_info(info['link'])
        desc = f"{info['name']} ({info['cat']})\n {'\n'.join(extra_info)}"
        desc = f"{desc} \n{info['region']}, {info['country']} \nFull information: {info['link']}"
        #   print(desc)
        date_start = datetime.strptime(dt,'%a %d %b %Y at %H:%M')
        tzx = timezone(country_timezones('gb')[0])
        date_start = tzx.localize(date_start)
        event = Event({
            'summary': race_dict[entry]['name'] + ' ('+race_dict[entry]['cat']+')',
            'uid':entry,
            'dtstart': date_start,
            'dtend': date_start + timedelta(hours=2),
            'dtstamp': datetime.now(),
            'description': desc,
            # 'location': venue,
        })

        cal.add_component(event)
        print(i+1/len(race_dict))
        # print(event)
    return cal

def run():
    core = 'https://races.fellrunner.org.uk/races/upcoming?page='

    race_dict = {}
    for pg in range(1,11):
        page = requests.get(core+str(pg))
        soup = bs4.BeautifulSoup(page.content,'html.parser')
        try:
            race_dict.update(get_races_from_page(soup))
        except Exception as e:
            print(e)

    cal = make_cal(race_dict)
    with open('fra_calendar.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ =="__main__":
    run()
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 17:13:31 2022

@author: jdconey
"""

import requests
import bs4
from icalendar import Calendar, Event
from pytz import timezone,country_timezones
from datetime import datetime,timedelta

def get_races_from_page(soup):
    races = soup.find_all('tr')
    race_dict={}
    for race in races:
        try:
            details = race.find_all('td')
            date = str(details[0]).replace('<td>','')
            date = date.replace('</td>','')
            name_link = str(details[1]).replace('<td class="titleCol"><a href="','')
            name_link = name_link.split('">')
            cat = str(details[2]).replace('<td>','')
            cat=cat.replace('</td>','')
            country = str(details[3]).replace('<td>','')
            country=country.replace('</td>','')
            region=str(details[4]).replace('<td>','')
            region=region.replace('</td>','')
            race_dict[name_link[0]] = {
                    'date':date,
                    'name':name_link[1].replace("</a></td>",''),
                    'cat':cat,
                    'country':country,
                    'region':region,
                    'link':'https://races.fellrunner.org.uk'+name_link[0]
                     }
        except:
            print('error')
    return race_dict

def extract_event_info(url):
    pg = requests.get(url)
    soup2 = bs4.BeautifulSoup(pg.content,'html.parser')
    listy = soup2.find_all("li")
    extra_info=[]
    for k in listy:
        if "Date &amp; time" in str(k):
            dt = str(k)
            dt = dt.replace("<li>\n<strong>Date &amp; time:</strong>",'')
            dt = dt.replace("</li>","")
            dt = dt.replace("  ","")
            dt = dt.replace('\n','')
            extra_info.append("Date & time: "+dt)
        if "Venue:" in str(k):
            venue = str(k)
            venue = venue.replace("<li>","")
            venue = venue.replace("</li>","")
            venue = venue.replace("<strong>","")
            venue = venue.replace("</strong>","")        
            venue = venue.replace("Venue:","")
            venue = venue.replace("\n","")
            venue = venue.replace("  ","")
        if "Distance:" in str(k) or "Climb:" in str(k) or "Venue:" in str(k) or "Grid reference:" in str(k) or "Skills:" in str(k) or "Minimum age:" in str(k)  or "Entry:" in str(k):
            info = str(k)
            info = info.replace("<li>","")
            info = info.replace("</li>","")
            info = info.replace("<strong>","")
            info = info.replace("</strong>","")
            info = info.replace("\n","")
            info = info.replace("  ","")
            extra_info.append(info)
    return dt,venue,extra_info
        
    

def make_cal(race_dict):
    cal = Calendar()
    cal.Timezone = 'TZID:Europe/London'
    i=0
    for entry in race_dict:
        event = Event()
        info = race_dict[entry]

        dt,venue,extra_info = extract_event_info(info['link'])
        desc = str(info['name']+' ('+info['cat']+')\n')
        for part in extra_info:
            desc = desc+str(part)+'\n'
        desc = desc+str(info['region'])+', '+str(info['country'])+'\nFull up to date information '+str(info['link'])
     #   print(desc)
        date_start = datetime.strptime(dt,'%a %d %b %Y at %H:%M')
        tzinfo = country_timezones('gb')[0]
        tzx = timezone(tzinfo)
        date_start = tzx.localize(date_start)
        date_end = date_start+timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=2, weeks=0)
        event.add('summary', race_dict[entry]['name'] + ' ('+race_dict[entry]['cat']+')')
        event.add('uid',entry)
        event.add('dtstart', date_start)
        event.add('dtend', date_end)
        event.add('dtstamp', datetime.now())
        event.add('location', venue)
        event.add('description', desc)
        cal.add_component(event)
        i=i+1
        print(i/len(race_dict))
       # print(event)
    return cal

core = 'https://races.fellrunner.org.uk/races/upcoming?page='
page = requests.get(core)
soup = bs4.BeautifulSoup(page.content, 'html.parser')
pgs=[]
for i in range(2,30):
    oot=soup.find_all('a',text=str(i))
    if len(oot)==1:
        pgs.append(i)
        
race_dict = get_races_from_page(soup)
for pg in pgs:
    page = requests.get(core+str(pg))
    soup = bs4.BeautifulSoup(page.content,'html.parser')
    race_dict.update(get_races_from_page(soup))

cal = make_cal(race_dict)

f = open('fra_calendar.ics', 'wb')
as_string = cal.to_ical()
as_string = as_string[:17]+bytes('BEGIN:VTIMEZONE\r\nTZID:Europe/London\r\nEND:VTIMEZONE\r\n', 'utf-8')+as_string[17:]
f.write(as_string)
f.close()
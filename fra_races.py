# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 17:13:31 2022

@author: jdconey
"""

import requests
import bs4
from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight
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
    full_str=''
    for k1 in listy:
        full_str=full_str+str(k1)
    extra_info=[]
    for k in listy:
        if "Date &amp; time" in str(k):
            dt = str(k)
            dt = dt.replace("<li>\n<strong>Date &amp; time:</strong>",'')
            dt = dt.replace("</li>","")
            dt = dt.replace("  ","")
            dt = dt.replace('\n','')
            extra_info.append("Date & time: "+dt)
        elif "Start time info" in str(k):
            if "Date &amp; time" not in full_str:
                for k2 in listy:
                    if 'Date' in str(k2):
                        dt2=str(k2)
                        dt2 = dt2.replace("<li>\n<strong>Date:</strong>",'')
                        dt2 = dt2.replace("</li>","")
                        dt2 = dt2.replace("  ","")
                        dt2 = dt2.replace('\n','')
                dt = str(k)
                dt = dt.replace("<li>\n<strong>Start time info:</strong>",'')
                dt = dt.replace("</li>","")
                dt = dt.replace("  ","")
                dt = dt.replace('\n','')
                dt = dt.replace('.',':')
                
                dt = dt2+' at '+dt
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
            venue = venue.replace(":","\:")
          #  venue = venue.encode()
#        if "Distance:" in str(k) or "Climb:" in str(k) or "Venue:" in str(k) or "Grid reference:" in str(k) or "Skills:" in str(k) or "Minimum age:" in str(k)  or "Entry:" in str(k):
        if "Distance:" in str(k) or "Climb:" in str(k) or "Grid reference:" in str(k) or "Entry" in str(k) or "entry" in str(k):
 
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
    cal['prodid'] = '-//Mozilla.org/NONSGML Mozilla Calendar V1.1//EN'
    cal['version'] = '2.0'
    cal['method'] = 'REQUEST'

    tzc = Timezone()
    tzc.add('tzid', 'Europe/London')
    tzc.add('x-lic-location', 'Europe/London')

    tzs = TimezoneStandard()
    tzs.add('tzname', 'GMT')
    tzs.add('TZOFFSETFROM',timedelta(hours=1))
    tzs.add('TZOFFSETTO',timedelta(hours=0))
    tzs.add('dtstart', datetime(1970, 10, 25, 2, 0, 0))
    tzs.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su', 'interval': '1'})

    tzd = TimezoneDaylight()
    tzd.add('tzname', 'BST')
    tzd.add('dtstart', datetime(1970, 3, 29, 1, 0, 0))
    tzd.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su', 'interval': '1'})
    tzd.add('TZOFFSETFROM', timedelta(hours=0))
    tzd.add('TZOFFSETTO', timedelta(hours=1))
    tzc.add_component(tzs)
    tzc.add_component(tzd)
    cal.add_component(tzc)

    i=0
    for entry in race_dict:
        event = Event()
        info = race_dict[entry]
     #   print(info['link'])
        dt,venue,extra_info = extract_event_info(info['link'])
        desc = info['name']+' ('+info['cat']+')'
        for part in extra_info:
            desc = desc+'\n'+str(part)
        desc = desc+'\n'+str(info['region'])+', '+str(info['country'])+'\nFull information: '+str(info['link'])
     #   print(desc)
        date_start = datetime.strptime(dt,'%a %d %b %Y at %H:%M')
        #date_start = datetime.strptime(info['date'],'%a %d %b %Y')
        tzinfo = country_timezones('gb')[0]
        tzx = timezone(tzinfo)
        date_start = tzx.localize(date_start)
        date_end = date_start+timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=2, weeks=0)
        event.add('summary', race_dict[entry]['name'] + ' ('+race_dict[entry]['cat']+')')
        event.add('uid',entry)
        event.add('dtstart', date_start)
        event.add('dtend', date_end)
        event.add('dtstamp', datetime.now())
     #   event.add('location', venue)
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
#for pg in [2]:
for pg in pgs:
    page = requests.get(core+str(pg))
    soup = bs4.BeautifulSoup(page.content,'html.parser')
    race_dict.update(get_races_from_page(soup))

cal = make_cal(race_dict)

f = open('fra_calendar.ics', 'wb')
as_string = cal.to_ical()
#as_string = as_string[:17]+bytes('\r\nPRODID:jdconey//EN\r\nVERSION:1.0\r\nBEGIN:VTIMEZONE\r\nTZID:Europe/London\r\nBEGIN:DAYLIGHT\r\nDTSTART:20200329T010000\r\nRRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU\r\nTZOFFSETFROM:0000\r\nTZOFFSETTO:0100\r\nTZNAME:BST\r\nEND:DAYLIGHT\r\nBEGIN:STANDARD\r\nDTSTART:20201025T010000\r\nRRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU\r\nTZOFFSETFROM:0100\r\nTZOFFSETTO:0000\r\nTZNAME:GMT\r\nEND:STANDARD\r\nEND:VTIMEZONE\r\n', 'utf-8')+as_string[17:]
f.write(as_string)
f.close()
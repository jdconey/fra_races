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

current_year = datetime.now().strftime('%Y')
current_year='2024'


def get_races_from_page(soup):
    race_dict = {}
    races = soup.find_all('tr')
    #race_dict={}
    for race in races:
        try:
            tbc=False
            details = race.find_all('td')
            date = str(details[0]).replace('<td>','')
            date = date.replace('</td>','')
            date = date.replace('<small>','')
            date = date.replace('</small>','')
            date = date.replace('<br/>','')
            date = date.replace('.00 noon','.00 pm')
            date = date.replace(' noon','.00 pm')
            date = date.replace("June","Jun")
            date = date.replace('0p','0 p')
            date = date.replace('5p','5 p')
            date = date.replace('st','')
            date=date.replace('nd','')
            date = date.replace('rd','')
            date = date.replace('th','')
            date = date.replace('From ','')
            date = date.replace(' a 2:30 ','')
            date = date.replace(':30','.30 ')
            date = date+current_year
            if '<span yle="color:red">TBC</span>' in date:
                date = date.replace('<span yle="color:red">TBC</span>','')
                tbc=True
            name_link = str(details[1]).replace('<td><a "="" href="','')
            name_link = name_link.replace('<td><a href="','')
            name_link = name_link.replace(' target="_blank" title="Links to external website"','')
            name_link = name_link.split('">')
            #name_link = name_link[0].split('">')
            #print(name_link)
            link = name_link[0]
            if '/racepage' in link:
                link = 'http://bofra.org.uk'+link
            else:
                link = link
            
            name2 = name_link[1].split('</a><br/><small>')
            name = name2[0]
            #print(name2)
            if 'Presentation Dinner' not in name:
                dist = name2[1].split('</small></td>')[0]
            else:
                dist = 'none'
            
            
            location = str(details[2]).replace('<td>','')
            location = location.replace('</td>','')
            
            cats = str(details[3]).replace('<td>','')
            cats = cats.replace('</td>','')
            
            champs = False
            if '#' in str(details[4]):
                champs=True
            
          
            race_dict['bofra_'+name] = {
                    'date':date,
                    'name':name,
                    'dist':dist,
                    'location':location,
                    'cats':cats,
                    'bofra_champs':'BOFRA Champs Race: '+str(champs),
                    'link':link,
                    'tbc':'TBC: '+str(tbc)
                     }
        except Exception as e:
            print('error',e)
    return race_dict

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
        desc = info['name']+' (BOFRA)'
        for part in info:
            desc = desc+'\n'+str(info[part])
     #   print(desc)
        print(info['date'])
        print(desc)
        try:
            date_start = datetime.strptime(info['date'],'%a %d %b%I.%M %p %Y')
        except Exception as e:
            print('trying again')
            print(e)
            try:
                date_start = datetime.strptime(info['date'],'%a %d %B%I.%M %p %Y')
            except Exception as e:
                print(e)
                print('nope nope nope')
        #date_start = datetime.strptime(info['date'],'%a %d %b %Y')
        tzinfo = country_timezones('gb')[0]
        tzx = timezone(tzinfo)
        date_start = tzx.localize(date_start)
        date_end = date_start+timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=2, weeks=0)
        event.add('summary', race_dict[entry]['name'] + ' (BOFRA)')
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

core = 'http://bofra.org.uk/racecalendar/'
page = requests.get(core)
soup = bs4.BeautifulSoup(page.content, 'html.parser')
pgs=[]
#for i in range(2,30):
#    oot=soup.find_all('a',text=str(i))
#    if len(oot)==1:
#        pgs.append(i)
 
race_dict = get_races_from_page(soup)
#for pg in [2]:


cal = make_cal(race_dict)

f = open('bofra_calendar.ics', 'wb')
as_string = cal.to_ical()
#as_string = as_string[:17]+bytes('\r\nPRODID:jdconey//EN\r\nVERSION:1.0\r\nBEGIN:VTIMEZONE\r\nTZID:Europe/London\r\nBEGIN:DAYLIGHT\r\nDTSTART:20200329T010000\r\nRRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU\r\nTZOFFSETFROM:0000\r\nTZOFFSETTO:0100\r\nTZNAME:BST\r\nEND:DAYLIGHT\r\nBEGIN:STANDARD\r\nDTSTART:20201025T010000\r\nRRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU\r\nTZOFFSETFROM:0100\r\nTZOFFSETTO:0000\r\nTZNAME:GMT\r\nEND:STANDARD\r\nEND:VTIMEZONE\r\n', 'utf-8')+as_string[17:]
f.write(as_string)
f.close()

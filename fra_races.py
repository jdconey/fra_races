# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 15:13:31 2022

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

def make_cal(race_dict):
    cal = Calendar()
    for entry in race_dict:
        event = Event()
        
        info = race_dict[entry]
        desc = info['name']+' ('+info['cat']+')\n'+info['region']+', '+info['country']+'\nMore Info: '+info['link']
        
        date_start = datetime.strptime(race_dict[entry]['date'],'%a %d %b %Y')
        tzinfo = country_timezones('gb')[0]
        tzx = timezone(tzinfo)
        date_start = tzx.localize(date_start)
        date_end = date_start+timedelta(days=0, seconds=59, microseconds=0, milliseconds=0, minutes=59, hours=23, weeks=0)
        event.add('summary', race_dict[entry]['name'] + ' ('+race_dict[entry]['cat']+')')
        event.add('dtstart', date_start)
        event.add('dtend', date_end)
        event.add('description', desc)
        cal.add_component(event)
       # print(event)
    return cal

core = 'https://races.fellrunner.org.uk/races/upcoming?page='
#page = requests.get(core)
#soup = bs4.BeautifulSoup(page.content, 'html.parser')
#pgs=[]
#for i in range(2,30):
#    oot=soup.find_all('a',text=str(i))
#    if len(oot)==1:
#        pgs.append(i)
        
#race_dict = get_races_from_page(soup)
#for pg in pgs:
#    page = requests.get(core+str(pg))
#    soup = bs4.BeautifulSoup(page.content,'html.parser')
#    race_dict.update(get_races_from_page(soup))

cal = make_cal(race_dict)

f = open('test_fra.ics', 'wb')
f.write(cal.to_ical())
f.close()
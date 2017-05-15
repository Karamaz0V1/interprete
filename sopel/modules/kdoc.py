import urllib.request
import calendar
import os

from datetime import datetime, timedelta
from pytz import timezone
from icalendar import Calendar, Event

from sopel import module

os.environ['TZ'] = 'Europe/Paris'
remote_cal = "https://kdoc.k0v1.xyz/remote.php/dav/public-calendars/5Q08PCZSSLP9Q2GQ?export"
local_cal = "calendar.ics"
lastseen = "lastseen.txt"

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

def printEvent(bot, component, begin, now):
    s = "* Le " + begin.strftime("%A %d à %Hh%m") +  "(dans " + strfdelta(begin-now,"{days} jours et {hours}h et {minutes} minutes") + "): " + component.get('summary') + ", " + component.get('location')
    bot.say (s)


@module.commands('kdoc')
def kdoc(bot, trigger):
    with open(".sopel/" + lastseen, 'w+') as f:
        lastget = f.read()
        now = calendar.timegm(datetime.now(timezone('Europe/Paris')).utctimetuple())
        if lastget == '':
            lastget = 0
        if ( (now - int(lastget)) > 3600):
            urllib.request.urlretrieve(remote_cal, local_cal)
            f.seek(0)
            f.write(str(now))
            f.truncate()
    f.close()


    g = open(local_cal,'rb')
    gcal = Calendar.from_ical(g.read())

    for component in gcal.walk():
        if component.name == "VEVENT":
            now = datetime.now(timezone('Europe/Paris'))
            begin = component.decoded('dtstart')
            end = component.decoded('dtend')

            if (type(begin) is not datetime):
                now = datetime.now(timezone('Europe/Paris')).date()
                if (timedelta(days=0) < (begin - now) < timedelta(days=5)):
                    prentEvent(bot, component, begin, now)
            else:
                if (timedelta(days=0) < (begin - now) < timedelta(days=5)):
                    prentEvent(bot, component, begin, now)

            g.close()

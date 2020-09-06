from Config import Config
import datetime
from urllib.parse import urlparse
import os
from vulcan._exam import Exam, ExamType
from vulcan._lesson import Lesson
from vulcan._homework import Homework

try:
    import vobject #pylint: disable=import-error
except ImportError:
    print("No module found: vobject. Trying to Install")
    try:
        os.system("pip install vobject")
        import vobject #pylint: disable=import-error
    except:
        print("Cannot install and enable: vobject!")

try:
    import caldav #pylint: disable=import-error
except ImportError:
    print("No module found: vobject. Trying to Install")
    try:
        os.system("pip install caldav")
        import caldav #pylint: disable=import-error
    except:
        print("Cannot install and enable: vobject!")

class CalDavManager:
    def __init__(self, config: Config):
        self.config = config
    
    def _prepare_cal(self):
        url_caldav2 = self.config.get("webdav_calendar")
        url_caldav = urlparse(url_caldav2)
        url_caldav2 = urlparse(url_caldav2)
        url_caldav = url_caldav._replace(netloc="{}:{}@{}".format(self.config.get("webdav_login"), self.config.get("webdav_password"), url_caldav.hostname))

        dav = caldav.DAVClient(url_caldav)
        principal = dav.principal()
        calendars = principal.calendars()

        cal = None

        if len(calendars) > 0:
            for calendar in calendars:
                calendar_parsed = urlparse(str(calendar.url))
                if calendar_parsed.hostname == url_caldav2.hostname and calendar_parsed.path == url_caldav2.path:
                        cal = calendar
        
        return cal
    
    def createExamEvent(self, exam: Exam, lesson: Lesson, title: str="", body: str=""):
        calendar = vobject.iCalendar()
        _title = exam.subject.name + ": " + exam.description
        if title != "":
            _title += " " + title
        
        calendar.add('vevent').add('summary').value = _title

        calendar.vevent.add('description').value = "Teacher: " + exam.teacher.name + "(" + exam.teacher.short + ")\n" + "Description: " + exam.description

        calendar.vevent.add("dtstart").value = datetime.datetime(lesson.from_.year, lesson.from_.month, lesson.from_.day, lesson.from_.hour, lesson.from_.minute, lesson.from_.second)
        calendar.vevent.add("dtend").value = datetime.datetime(lesson.to.year, lesson.to.month, lesson.to.day, lesson.to.hour, lesson.to.minute, lesson.to.second)
        if exam.type == ExamType.EXAM:
            valarm = calendar.vevent.add('valarm')
            valarm.add('action').value = "AUDIO"
            valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=14)
            valarm = calendar.vevent.add('valarm')
            valarm.add('action').value = "AUDIO"
            valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=7)
            valarm = calendar.vevent.add('valarm')
            valarm.add('action').value = "AUDIO"
            valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=3)
            valarm = calendar.vevent.add('valarm')
            valarm.add('action').value = "AUDIO"
            valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=2)
            valarm = calendar.vevent.add('valarm')
            valarm.add('action').value = "AUDIO"
            valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=1)
            valarm = calendar.vevent.add('valarm')
            valarm.add('action').value = "AUDIO"
            valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=0)
        elif exam.type == ExamType.SHORT_TEST:
            valarm = calendar.vevent.add('valarm')
            valarm.add('action').value = "AUDIO"
            valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=3)
            valarm = calendar.vevent.add('valarm')
            valarm.add('action').value = "AUDIO"
            valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=2)
            valarm = calendar.vevent.add('valarm')
            valarm.add('action').value = "AUDIO"
            valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=1)
            valarm = calendar.vevent.add('valarm')
            valarm.add('action').value = "AUDIO"
            valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=0)
        else:
            valarm = calendar.vevent.add('valarm')
            valarm.add('action').value = "AUDIO"
            valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=1)
            valarm = calendar.vevent.add('valarm')
            valarm.add('action').value = "AUDIO"
            valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=0)
        
        return calendar
    
    
    def createHomeworkEvent(self, homework: Homework, lesson: Lesson, title: str="", body: str=""):
        calendar = vobject.iCalendar()
        _title = homework.subject.name + ": " + homework.description
        if title != "":
            _title += " " + title
        
        calendar.add('vevent').add('summary').value = _title

        calendar.vevent.add('description').value = "Teacher: " + homework.teacher.name + "(" + homework.teacher.short + ")\n" + "Description: " + homework.description

        calendar.vevent.add("dtstart").value = datetime.datetime(lesson.from_.year, lesson.from_.month, lesson.from_.day, lesson.from_.hour, lesson.from_.minute, lesson.from_.second)
        calendar.vevent.add("dtend").value = datetime.datetime(lesson.to.year, lesson.to.month, lesson.to.day, lesson.to.hour, lesson.to.minute, lesson.to.second)
        
        valarm = calendar.vevent.add('valarm')
        valarm.add('action').value = "AUDIO"
        valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=1)
        valarm = calendar.vevent.add('valarm')
        valarm.add('action').value = "AUDIO"
        valarm.add("trigger").value = lesson.from_ - datetime.timedelta(days=0)
        
        return calendar

    def sendEvent(self, event: vobject.icalendar.VCalendar2_0):
        cal = self._prepare_cal()
        start = event.getSortedChildren()[0].getChildValue("dstart")
        end = event.getSortedChildren()[0].getChildValue("dend")
        search = cal.date_search(start, end)

        if len(search) <= 0:
            return cal.add_event(event)
        else:
            search = search[0].vobject_instance.getSortedChildren()
            for x in search:
                try:
                    x.getChildValue("description")
                    search = x
                    break
                except:
                    continue
            vo = event.getSortedChildren()[0]
            if not search.getChildValue("description") == vo.getChildValue("description") or not search.getChildValue("summary") == vo.getChildValue("summary"):
                cal.date_search(start, end)[0].delete()
                return cal.add_event(event)
            else:
                return None
        
    def compareEvents(self, events: list):
        cal = self._prepare_cal()
        for calEvent in cal.events():
            toDelete = True
            tmpEvent = calEvent.vobject_instance.getSortedChildren()
            for x in tmpEvent:
                try:
                    x.getChildValue("description")
                    tmpEvent = x
                    break
                except:
                    continue
            for myEvent in events:
                myEvent = myEvent.getSortedChildren()[0]
                if tmpEvent.getChildValue("description") == myEvent.getChildValue("description") and tmpEvent.getChildValue("summary") == myEvent.getChildValue("summary"):
                    toDelete = False
            if toDelete:
                calEvent.delete()
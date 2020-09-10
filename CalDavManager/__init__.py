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

class CalDavType:
    GOOGLE = 0
    NEXTCLOUD = 1

class CalDavManager:
    def __init__(self, config: Config):
        self.config = config
    
    def _get_caldav_type(self):
        url = urlparse(self.config.get("webdav_calendar"))
        if("google" in url.hostname):
            return CalDavType.GOOGLE
        elif("nextcloud" in url.hostname):
            return CalDavType.NEXTCLOUD
        else:
            return -1
    
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
            if self._get_caldav_type() == CalDavType.NEXTCLOUD:
                for calendar in calendars:
                    calendar_parsed = urlparse(str(calendar.url))
                    if calendar_parsed.hostname == url_caldav2.hostname and calendar_parsed.path == url_caldav2.path:
                            cal = calendar
            
                if cal == None:
                    cal = calendars[0]
            elif self._get_caldav_type() == CalDavType.GOOGLE:
                cal = calendars[0]
            else:
                raise Exception("Not valid URL! Only: Google and Nextcloud are compatible!")
        
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
        start = event.getSortedChildren()[0].getChildValue("dtstart") + datetime.timedelta(hours=2)
        end = event.getSortedChildren()[0].getChildValue("dtend") + datetime.timedelta(hours=2)
        search = cal.date_search(start, end)
        print(start, end)
        print(search)

        if len(search) <= 0:
            return cal.add_event(event)
        else:
            if self._get_caldav_type() == CalDavType.NEXTCLOUD:
                search = search[0].vobject_instance.getSortedChildren()
                for x in search:
                    try:
                        x.getChildValue("summary")
                        search = x
                        break
                    except:
                        continue
                vo = event.getSortedChildren()[0]
                if not search.getChildValue("summary") == vo.getChildValue("summary"):
                    cal.date_search(start, end)[0].delete()
                    return cal.add_event(event)
                else:
                    return None
            elif self._get_caldav_type() == CalDavType.GOOGLE:
                found = False
                for x in search:
                    for y in x.vobject_instance.getSortedChildren():
                        try:
                            if y.getChildValue("summary") == None:
                                raise Exception()
                            search = y
                            found = True
                            break
                        except:
                            continue
                
                if not found:
                    for x in search:
                        x.delete()
                        print("Removing event!")
                    return cal.add_event(event)
                    # return None

                vo = event.getSortedChildren()[0]
                # print("\n", search.getChildValue("summary"), "\n")
                if not search.getChildValue("summary") == vo.getChildValue("summary"):
                    cal.date_search(start, end)[0].delete()
                    return cal.add_event(event)
                else:
                    return None
            else:
                return None
        
    def compareEvents(self, events: list):
        cal = self._prepare_cal()
        for calEvent in cal.events():
            toDelete = True
            tmpEvent = calEvent.vobject_instance.getSortedChildren()
            found = False
            for x in tmpEvent:
                try:
                    if x.getChildValue("summary") == None:
                        raise Exception()
                    tmpEvent = x
                    found = True
                    break
                except:
                    continue
            if not found:
                continue
            for myEvent in events:
                myEvent = myEvent.getSortedChildren()[0]
                # print("\n", myEvent, "\n")
                # print("\n", tmpEvent.getChildValue("description"), "\n")
                # print("\n", myEvent.getChildValue("description"), "\n")
                try:
                    if tmpEvent.getChildValue("description") == myEvent.getChildValue("description") and tmpEvent.getChildValue("summary") == myEvent.getChildValue("summary"):
                        toDelete = False
                    elif not "Teacher: " in tmpEvent.getChildValue("description"):
                        toDelete = False
                except:
                    continue
            if toDelete:
                print("Removing:", calEvent)
                calEvent.delete()
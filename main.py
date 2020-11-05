#!/usr/bin/env python3

#####################################################################################
# __  __        _                _                                                  #
#|  \/  | __ _ (_)_ __ ___   ___| |__       Github: https://github.majroch.pl       #
#| |\/| |/ _` || | '__/ _ \ / __| '_ \      Git Repo: https://git.majroch.pl        #
#| |  | | (_| || | | | (_) | (__| | | |     Homepage: https://majroch.pl            #
#|_|  |_|\__,_|/ |_|  \___/ \___|_| |_|                                             #
#            |__/                                                                   #
#####################################################################################

from vulcan import Vulcan
import json, datetime, time
from CalDavManager import CalDavManager
from Config import Config

config = Config("main.cfg")
caldav = CalDavManager(config)

try:
    with open(config.get("cert"), "r") as file:
        cert = json.load(file)
except FileNotFoundError:
    print("Cannot find Cert! Creating one:")
    token = input("Enter Token: ")
    symbol = input("Enter Symbol: ")
    pin = input("Enter PIN: ")

    cert = Vulcan.register(token, symbol, pin)

    if cert != None:
        with open(config.get("cert"), "w") as file:
            file.write(json.dumps(cert.json))
    else:
        print("No cert found!")
        exit()
    
vulcan = Vulcan(cert)

while True:
    dates = []
    for x in range(30):
        dates.append(datetime.date.today() + datetime.timedelta(days=x))

    exams = []
    for date in dates:
        for exam in vulcan.get_exams(date=date):
            lessons = []
            for lesson in vulcan.get_lessons(date=date):
                if exam.subject == lesson.subject:
                    lessons.append(lesson)
            if len(lessons) > 0:
                exams.append([exam, lessons])

    events = []
    for exam in exams:
        if len(exam[1]) > 0:
            events.append(caldav.createExamEvent(exam[0], exam[1][0]))

    homeworks = []
    for date in dates:
        for homework in vulcan.get_homework(date=date):
            lessons = []
            for lesson in vulcan.get_lessons(date=date):
                if homework.subject == lesson.subject:
                    lessons.append(lesson)
            if len(lessons) > 0:
                homeworks.append([homework, lessons])
    
    for homework in homeworks:
        if len(homework[1]) > 0:
            events.append(caldav.createHomeworkEvent(homework[0], homework[1][0]))

    for event in events:
        if event:
            if caldav.sendEvent(event):
                print("Sent!")

    caldav.compareEvents(events)

    print("Sleep for 1 hour!")
    time.sleep(3600)

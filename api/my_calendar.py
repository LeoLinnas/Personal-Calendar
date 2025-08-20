from tabulate import *
from datetime import *
import json
import os

CALENDAR_FILE = "calendar.json"

def check_create_file():

    if not os.path.isfile(CALENDAR_FILE):
        with open(CALENDAR_FILE, "w") as calendar:
            calendar.write("{}")

    elif os.path.isfile(CALENDAR_FILE):
        with open("calendar_copy.json", "w") as copy:
            original = open(CALENDAR_FILE, "r")
            copy.write(original.read())

class Activity():

    def __init__(self, 
                 date, 
                 title, 
                 start_time : str, 
                 *,
                 duration : str|None = None, 
                 end_time : str|None = None, 
                 notes : str = "", 
                 priority : str = "",
                 tag : str = ""
                ):

        self.date : datetime = datetime.strptime(date, "%Y-%m-%d")
        self.title : str = title
        self.start_time : datetime = datetime.strptime(start_time, "%H:%M")
        self.notes : str = notes
        self.priority : int = int(priority or 0)
        self.tag : str = tag

        # här kan saker som plats, personer, kontakt info och annat också läggas till för intressanta funktioner
        # som att automatiskt meddela någon om man blir tvungen att skriva över en aktivitet med denna

        # Räkna ut och sätt end och duration
        if not end_time and duration:
            t = datetime.strptime(duration, "%H:%M")
            self.duration : timedelta = timedelta(hours=t.hour, minutes=t.minute)
            self.end_time : datetime = self.start_time + self.duration

        elif not duration and end_time:
            self.end_time : datetime = datetime.strptime(end_time, "%H:%M")
            self.duration : timedelta = self.end_time - self.start_time

        else:
            t = datetime.strptime(duration, "%H:%M")
            self.duration : timedelta = timedelta(hours=t.hour, minutes=t.minute)
            self.end_time : datetime = datetime.strptime(end_time, "%H:%M")

    def to_dictionary(self):
        return {
            "date" : datetime.strftime(self.date, "%Y-%m-%d"), 
            "title" : self.title,
            "start_time" : datetime.strftime(self.start_time, "%H:%M"),
            "duration" : ":".join(str(self.duration).split(":")[:2]),
            "end_time" : datetime.strftime(self.end_time, "%H:%M"),
            "notes" : self.notes,
            "priority" : str(self.priority),
            "tag" : self.tag
        }
    
    def __str__(self):

        return (
            f"Aktivitet: {self.title}\n"
            f"Startar: {datetime.strftime(self.start_time, "%H:%M")}\n"
            f"Slutar: {datetime.strftime(self.end_time, "%H:%M")}\n"
            f"Längd: {str(self.duration)}\n"
            f"{f"Anteckningar: {self.notes}\n" if self.notes != "" else ""}"
            f"{f"Tag: {self.tag}\n" if self.tag != "" else ""}"
        )


class Calendar():

    def __init__(self):
        
        self.activities = self.load_calendar()

    def add_activity(self):
        print("----- Lägg till aktivitet -----")

        title = input("Aktivitet titel: ")
        date = input("Datum för aktivitet (yyyy-mm-dd): ")
        start_time = input("Start tid(hh:mm): ")


        print("\nMinst längd eller slut tid måste vara vald")

        try: 
            duration = input("Aktivitetens längd (hh:mm): ")
        except:
            duration = None

        try:
            end_time = input("Slut tid(hh:mm): ")
        except: 
            end_time = None

        print("\nResterande är valfritt:")
        notes = input("Anteckningar: ")

        try:
            priority = input("Välj priorietet (1-5, 0 är standard): ")
        except:
            priority = 0

        activity = Activity(date = date, 
                            title = title,
                            start_time = start_time,
                            duration = duration,
                            end_time = end_time,
                            notes = notes,
                            priority = priority,
                        )
        
        self.try_to_fit_activity(activity)

    def remove_activity(self, activity : Activity):

        date_key = datetime.strftime(activity.date, "%Y-%m-%d")

        self.activities[date_key].remove(activity)

        if self.activities[activity.date] == []:
            self.activities.pop(date_key)

        print(f"Aktivitet {activity.title} är borttagen")

    def try_to_fit_activity(self, new_activity : Activity):

        def overlapping(activity_a : Activity, activity_b : Activity) -> bool:
            
            start_a_overlapp = activity_a.start_time >= activity_b.start_time and activity_a.start_time < activity_b.end_time
            end_a_overlapp = activity_a.end_time > activity_b.start_time and activity_a.end_time <= activity_b.end_time

            return (start_a_overlapp or end_a_overlapp)
        
        if new_activity.date not in self.activities: 
            self.activities[new_activity.date] = [new_activity]
        
        elif self.activities[new_activity.date] == []:
            self.activities[new_activity.date].append(new_activity)

        else:
            planned_activity : Activity

            for planned_activity in self.activities[new_activity.date]:

                if overlapping(new_activity, planned_activity):

                    if planned_activity.priority == new_activity.priority:
                        new_activity.tag = "inspect"
                        continue
                    
                    elif new_activity.priority == 0:

                        if new_activity.start_time >= planned_activity.start_time:
                            new_activity.start_time = planned_activity.end_time

                            changed_time = "start"
                            new_time = datetime.strftime(new_activity.start_time, "%H:%M")

                        elif new_activity.end_time >= planned_activity.end_time:
                            new_activity.end_time = planned_activity.start_time

                            changed_time = "slut"
                            new_time = datetime.strftime(new_activity.end_time, "%H:%M")


                        print(f"Aktivitet redan plannerad, {changed_time}tid ändrad till {new_time}")
                        continue
                    
                    #om de inte har samma eller en är noll och andra hägre kolla högsta och vilken den är
                    highest_prio_activity = max(new_activity, planned_activity, key=lambda x: x.priority) #tänk på om new_activity alltid borde bli highest om de är samma
                
                    if highest_prio_activity is planned_activity: 
                        if planned_activity.start_time >= new_activity.start_time:
                            new_activity.tag += "end_early_"
                            
                        elif planned_activity.end_time >= new_activity.start_time:
                            new_activity.tag += "start_late_"

                        print("Gammla aktiviteten har högre prio")

                    elif highest_prio_activity is new_activity:

                        if new_activity.start_time >= planned_activity.start_time:
                            planned_activity.tag += "end_early_"

                        elif new_activity.end_time >= planned_activity.start_time:
                            planned_activity.tag += "start_late_"
                        
                        print("Ny aktiviteten har högre prio")

            self.activities[new_activity.date].append(new_activity)
            self.activities[new_activity.date] = sorted(self.activities[new_activity.date], key=lambda x: x.start_time)

    def load_calendar(self):
        objects = {}

        # undra om detta ens funkar
        with open(CALENDAR_FILE, "r") as calendar:
            activities = json.loads(calendar.read())

            for date in activities:
                date_object = datetime.strptime(date, "%Y-%m-%d")
                objects[date_object] = []
                for activity in activities[date]:
                    objects[date_object].append(Activity(date = activity["date"], 
                                                           title = activity["title"],
                                                           start_time = activity["start_time"],
                                                           duration = activity["duration"],
                                                           end_time = activity["end_time"],
                                                           notes = activity["notes"],
                                                           priority = activity["priority"],
                                                           tag = activity["tag"]
                                                        ))

            calendar.close()
        return objects

    def to_dict(self) -> dict:
        calendar_as_dict = {}

        for key in self.activities:
            calendar_as_dict[datetime.strftime(key, "%Y-%m-%d")] = []

            for value in self.activities[key]:
                calendar_as_dict[datetime.strftime(key, "%Y-%m-%d")].append(value.to_dictionary())

        return calendar_as_dict

    def save_to_file(self):

        with open(CALENDAR_FILE, "w") as file:
            file.write(json.dumps(self.to_dict(), indent=4, sort_keys=True))

    def __str__(self):
        activities = self.activities
        table = tabulate(activities, headers=[datetime.strftime(x, "%Y-%m-%d") for x in activities], tablefmt="grid")
        
        return (
            f"\n"
            f"{table}"
            f"\n"
        )

check_create_file()
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from supabase import create_client
from dotenv import load_dotenv
import os
import pyttsx3
import time

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

latest_reminder = None

# -----------------------------
# VOICE SETUP
# -----------------------------

engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)


# -----------------------------
# PREVENT DUPLICATE REMINDERS
# -----------------------------

reminded_tasks = set()
reminded_events = set()


# -----------------------------
# SPEAK FUNCTION
# -----------------------------

def speak(message):

    print("🔊 SPEAKING:", message)

    engine.say(message)
    engine.runAndWait()


# -----------------------------
# TRIGGER REMINDER
# -----------------------------

def trigger_reminder(
    reminder_id,
    title,
    reminder_type,
    reminder_time
):

    global latest_reminder

    if reminder_type == "task":

        message = (
            f"Patricia, it is time "
            f"for {title}."
        )

    else:

        message = (
            f"Patricia, you have an upcoming "
            f"event: {title}."
        )

    print()
    print("===========================")
    print("🔔 REMINDER!")
    print("🎵 MUSIC FIRST")
    print(f"🔊 {message}")
    print("===========================")
    print()

    # Send reminder information
    # to the dashboard
    latest_reminder = {
        "id": reminder_id,
        "title": title,
        "message": message,
        "time": reminder_time,
        "type": reminder_type
    }

    # Give the browser time to start
    # the background music
    time.sleep(5)

    # Voice speaks twice
    speak(message)
    speak(message)


# -----------------------------
# CHECK TASK REMINDERS
# -----------------------------

def check_task_reminders():

    global latest_reminder

    now = datetime.now()

    today = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")

    print(
        f"⏰ Checking tasks: "
        f"{today} {current_time}"
    )

    try:

        response = (
            supabase
            .table("tasks")
            .select("*")
            .eq("task_date", today)
            .eq("reminder_enabled", True)
            .eq("status", "pending")
            .execute()
        )

        tasks = response.data

        print(
            f"📋 Today's pending tasks: "
            f"{len(tasks)}"
        )

        for task in tasks:

            task_id = task["id"]
            task_title = task["title"]

            task_time = task["task_time"]

            if isinstance(task_time, str):
                task_time = task_time[:5]

            reminder_key = (
                f"{task_id}-{today}"
            )

            print(
                f"   Task: {task_title} "
                f"| Time: {task_time}"
            )

            if (
                task_time == current_time
                and reminder_key
                not in reminded_tasks
            ):

                trigger_reminder(
                    task_id,
                    task_title,
                    "task",
                    current_time
                )

                reminded_tasks.add(
                    reminder_key
                )

    except Exception as error:

        print(
            f"❌ Task reminder error: "
            f"{error}"
        )


# -----------------------------
# CHECK EVENT REMINDERS
# -----------------------------

def check_event_reminders():

    now = datetime.now()

    print(
        f"📅 Checking event reminders: "
        f"{now.strftime('%Y-%m-%d %H:%M')}"
    )

    try:

        response = (
            supabase
            .table("events")
            .select("*")
            .eq("reminder_enabled", True)
            .eq("status", "upcoming")
            .execute()
        )

        events = response.data

        print(
            f"📆 Upcoming events: "
            f"{len(events)}"
        )

        for event in events:

            event_id = event["id"]
            event_title = event["title"]

            event_date = event["event_date"]
            event_time = event["event_time"]

            # Convert database values to strings
            event_date = str(event_date)
            event_time = str(event_time)

            # Remove seconds from time
            event_time_short = event_time[:5]

            # Create event date and time
            event_datetime = datetime.strptime(
                f"{event_date} {event_time_short}",
                "%Y-%m-%d %H:%M"
            )

            reminder_days = event.get(
                "reminder_before_days",
                0
            )

            reminder_minutes = event.get(
                "reminder_before_minutes",
                0
            )

            if reminder_days is None:
                reminder_days = 0

            if reminder_minutes is None:
                reminder_minutes = 0

            reminder_days = int(
                reminder_days
            )

            reminder_minutes = int(
                reminder_minutes
            )

            # --------------------------------
            # DAYS BEFORE REMINDER
            # --------------------------------

            if reminder_days > 0:

                reminder_datetime = (
                    event_datetime
                    - __import__("datetime").timedelta(
                        days=reminder_days
                    )
                )

                reminder_key = (
                    f"{event_id}-days-"
                    f"{reminder_days}-"
                    f"{event_date}"
                )

                print(
                    f"   Event: {event_title} "
                    f"| Reminder: "
                    f"{reminder_days} day(s) before"
                )

                if (
                    now.strftime("%Y-%m-%d %H:%M")
                    ==
                    reminder_datetime.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    and reminder_key
                    not in reminded_events
                ):

                    trigger_reminder(
                        event_id,
                        event_title,
                        "event",
                        now.strftime(
                            "%H:%M"
                        )
                    )

                    reminded_events.add(
                        reminder_key
                    )

            # --------------------------------
            # MINUTES BEFORE REMINDER
            # --------------------------------

            elif reminder_minutes > 0:

                from datetime import timedelta

                reminder_datetime = (
                    event_datetime
                    - timedelta(
                        minutes=reminder_minutes
                    )
                )

                reminder_key = (
                    f"{event_id}-minutes-"
                    f"{reminder_minutes}-"
                    f"{event_date}"
                )

                print(
                    f"   Event: {event_title} "
                    f"| Reminder: "
                    f"{reminder_minutes} "
                    f"minute(s) before"
                )

                if (
                    now.strftime("%Y-%m-%d %H:%M")
                    ==
                    reminder_datetime.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    and reminder_key
                    not in reminded_events
                ):

                    trigger_reminder(
                        event_id,
                        event_title,
                        "event",
                        now.strftime(
                            "%H:%M"
                        )
                    )

                    reminded_events.add(
                        reminder_key
                    )

    except Exception as error:

        print(
            f"❌ Event reminder error: "
            f"{error}"
        )


# -----------------------------
# CHECK ALL REMINDERS
# -----------------------------

def check_reminders():

    check_task_reminders()

    check_event_reminders()


# -----------------------------
# START REMINDER ENGINE
# -----------------------------

scheduler = BackgroundScheduler()

scheduler.add_job(
    check_reminders,
    "interval",
    seconds=10
)

scheduler.start()

print()
print(
    "🔔 Patricia's Reminder Engine started!"
)
print(
    "⏰ Checking for reminders every 10 seconds..."
)
print()
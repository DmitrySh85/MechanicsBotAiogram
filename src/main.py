import asyncio
import logging
import sys
from scheduler import (
    send_day_reminder_to_masters,
    send_evening_reminder_to_masters,
    send_day_reminder_to_admins,
    send_evening_reminder_to_admins,
    save_discipline_violation,
    get_monthly_report,
    check_general_cleaning_and_send_messages,
    check_one_day_left_before_general_cleaning_and_send_message,
    remind_to_admin_about_general_cleaning,
    send_working_masters_for_tomorrow_request
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from settings import START_WORK_TIME, END_WORK_TIME, REMINDER_OFFSET, ADMIN_NOTIFICATION_DELAY
from services.handlers_services import convert_string_to_time_with_offset

from dispatcher import start_polling


logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

time_start = convert_string_to_time_with_offset(START_WORK_TIME, REMINDER_OFFSET)
admin_notification_time_start = convert_string_to_time_with_offset(START_WORK_TIME, str(int(REMINDER_OFFSET) + ADMIN_NOTIFICATION_DELAY))
time_end = convert_string_to_time_with_offset(END_WORK_TIME, REMINDER_OFFSET)
admin_notification_time_end = convert_string_to_time_with_offset(END_WORK_TIME, str(int(REMINDER_OFFSET) + ADMIN_NOTIFICATION_DELAY))


scheduler.add_job(
    send_day_reminder_to_masters,
    trigger='cron',
    hour=time_start.hour,
    minute=time_start.minute
)
scheduler.add_job(
    send_day_reminder_to_admins,
    trigger='cron',
    hour=admin_notification_time_start.hour,
    minute=admin_notification_time_start.minute,
)
scheduler.add_job(
    save_discipline_violation,
    trigger='cron',
    hour=admin_notification_time_start.hour,
    minute=admin_notification_time_start.minute,
)
scheduler.add_job(
    send_evening_reminder_to_masters,
    trigger='cron',
    hour=time_end.hour,
    minute=time_end.minute,
)
scheduler.add_job(
    send_evening_reminder_to_admins,
    trigger='cron',
    hour=admin_notification_time_end.hour,
    minute=admin_notification_time_end.minute,
)
scheduler.add_job(
    save_discipline_violation,
    trigger='cron',
    hour=admin_notification_time_end.hour,
    minute=admin_notification_time_end.minute,
)
scheduler.add_job(
    get_monthly_report,
    trigger='cron',
    hour=10,
    minute=0,
    day=1
)
scheduler.add_job(
    check_one_day_left_before_general_cleaning_and_send_message,
    trigger='cron',
    hour=10,
    minute=0
)
scheduler.add_job(
    check_general_cleaning_and_send_messages,
    trigger='cron',
    hour=10,
    minute=0
)
scheduler.add_job(
    remind_to_admin_about_general_cleaning,
    trigger='cron',
    hour=10,
    minute=1,
    day=1
)
scheduler.add_job(
    send_working_masters_for_tomorrow_request,
    trigger='cron',
    hour=18,
    minute=0
)


if __name__ == "__main__":
    scheduler.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_polling())

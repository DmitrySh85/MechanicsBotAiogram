import asyncio
import logging
from scheduler import send_reminder_to_masters, send_reminder_to_admins, save_discipline_violation
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from settings import START_WORK_TIME, END_WORK_TIME, REMINDER_OFFSET, ADMIN_NOTIFICATION_DELAY
from services.handlers_services import convert_string_to_time_with_offset

from dispatcher import start_polling

logging.basicConfig(level=logging.INFO, filename="mechanics_bot.log")

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

time_start = convert_string_to_time_with_offset(START_WORK_TIME, REMINDER_OFFSET)
admin_notification_time_start = convert_string_to_time_with_offset(START_WORK_TIME, str(int(REMINDER_OFFSET) + ADMIN_NOTIFICATION_DELAY))
time_end = convert_string_to_time_with_offset(END_WORK_TIME, REMINDER_OFFSET)
admin_notification_time_end = convert_string_to_time_with_offset(END_WORK_TIME, str(int(REMINDER_OFFSET) + ADMIN_NOTIFICATION_DELAY))


scheduler.add_job(send_reminder_to_masters, trigger='cron', hour=time_start.hour, minute=time_start.minute, day_of_week='mon-fri')
scheduler.add_job(send_reminder_to_admins, trigger='cron',
                  hour=admin_notification_time_start.hour, minute=admin_notification_time_start.minute,
                  day_of_week='mon-fri')
scheduler.add_job(save_discipline_violation, trigger='cron',
                  hour=admin_notification_time_start.hour, minute=admin_notification_time_start.minute,
                  day_of_week='mon-fri')
scheduler.add_job(send_reminder_to_masters, trigger='cron', hour=time_end.hour, minute=time_end.minute, day_of_week='mon-fri')
scheduler.add_job(send_reminder_to_admins, trigger='cron',
                  hour=admin_notification_time_end.hour, minute=admin_notification_time_end.minute,
                  day_of_week='mon-fri')
scheduler.add_job(save_discipline_violation, trigger='cron',
                  hour=admin_notification_time_end.hour, minute=admin_notification_time_end.minute,
                  day_of_week='mon-fri')

if __name__ == "__main__":
    scheduler.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_polling())

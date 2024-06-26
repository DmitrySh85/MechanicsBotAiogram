import asyncio
import logging
from scheduler import send_reminder_to_masters
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dispatcher import start_polling

logging.basicConfig(level=logging.INFO, filename="mechanics_bot.log")

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
scheduler.add_job(send_reminder_to_masters, trigger='cron', hour=9, minute=20, day_of_week='mon-fri')
scheduler.add_job(send_reminder_to_masters, trigger='cron', hour=18, minute=10, day_of_week='mon-fri')


if __name__ == "__main__":
    scheduler.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_polling())

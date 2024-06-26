from dispatcher import bot
from services.schedule_services import check_masters_not_send_photo
import pytz
import logging
from datetime import datetime, timedelta
from static_text.static_text import MISSING_PHOTO_TEXT



async def send_reminder_to_masters():
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz)
    start_time = now - timedelta(minutes=30)
    masters_tg_ids = await check_masters_not_send_photo(start_time, now)
    logging.info(f"Не прислали фото: {masters_tg_ids}" )
    for tg_id in masters_tg_ids:
        await bot.send_message(tg_id.tg_id, MISSING_PHOTO_TEXT)
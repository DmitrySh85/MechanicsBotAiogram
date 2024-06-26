import os
from dotenv import load_dotenv
load_dotenv()


DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
BOT_TOKEN = os.environ.get("BOT_TOKEN")

START_WORK_TIME = os.environ.get("START_WORK_TIME")
END_WORK_TIME = os.environ.get("END_WORK_TIME")
REMINDER_OFFSET = os.environ.get("REMINDER_OFFSET")
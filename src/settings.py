import os
from dotenv import load_dotenv
load_dotenv()


DB_HOST: str = os.environ.get("DB_HOST")
DB_PORT: str = os.environ.get("DB_PORT")
DB_NAME: str = os.environ.get("DB_NAME")
DB_USER: str = os.environ.get("DB_USER")
DB_PASS: str = os.environ.get("DB_PASS")
DB_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
BOT_TOKEN: str = os.environ.get("BOT_TOKEN")
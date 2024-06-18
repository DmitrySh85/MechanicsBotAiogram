import asyncio
import logging
from dispatcher import start_polling

logging.basicConfig(level=logging.INFO, filename="mechanics_bot.log")

if __name__ == "__main__":
    asyncio.run(start_polling())

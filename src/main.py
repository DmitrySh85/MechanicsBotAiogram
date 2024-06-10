import asyncio

from dispatcher import start_polling


if __name__ == "__main__":
    asyncio.run(start_polling())
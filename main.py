import moea
import asyncio

bot = moea.init()

if __name__ == '__main__':
    # bot.run_multi_clients(TEST_ROOM_IDS)
    # asyncio.run(bot.run_multi_clients(TEST_ROOM_IDS))
    # bot.run_async()
    asyncio.run(bot.run_async())


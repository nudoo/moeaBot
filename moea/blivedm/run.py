import blivedm
import asyncio
import random
import _thread

TEST_ROOM_IDS = [
    27712979,
    23808183,
    25673317,
    22048043,
]

class MoeaBot(object):
    def __init__(self, config_object=None):
        """
        You should NOT instantiate a MoeaBot!
        This is for intellisense code completion.
        Use `hoshino.init()` instead.
        """
        super().__init__()
        # raise Exception("You should NOT instantiate a HoshinoBot! Use `hoshino.init()` instead.")

    async def run_multi_clients(self, roomid):
        """
        演示同时监听多个直播间
        """
        clients = [blivedm.BLiveClient(room_id) for room_id in TEST_ROOM_IDS]
        handler = MyHandler()
        for client in clients:
            client.add_handler(handler)
            client.start()

        try:
            await asyncio.gather(*(
                client.join() for client in clients
            ))
        finally:
            await asyncio.gather(*(
                client.stop_and_close() for client in clients
            ))

    async def run(self, roomid):
        asyncio.run(self.run_multi_clients(roomid))


class MyHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
    #
    # # 入场消息回调
    # async def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
    #     print(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
    #           f" uname={command['data']['uname']}")
    # _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

    async def _on_heartbeat(self, client: blivedm.BLiveClient, message: blivedm.HeartbeatMessage):
        print(f'[{client.room_id}] 当前人气值：{message.popularity}')

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        print(f'[{client.room_id}] {message.uname}：{message.msg}')

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        print(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
              f' （{message.coin_type}瓜子x{message.total_coin}）')

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        print(f'[{client.room_id}] {message.username} 购买{message.gift_name}')

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        print(f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')


if __name__ == '__main__':
    bot = MoeaBot()
    bot.run(TEST_ROOM_IDS)
    # asyncio.run(bot.run_multi_clients(TEST_ROOM_IDS))
    # asyncio.run(run_multi_clients())
    # _thread.start_new_thread(asyncio.run, (run_multi_clients(),))

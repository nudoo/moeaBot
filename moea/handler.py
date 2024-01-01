from moea.blivedm import blivedm
from moea import trigger
import requests
import json
from queue import Queue, PriorityQueue
import random

roomID = 1360104
# 最优先队列、sc、礼物、弹幕队列
topQue = Queue(maxsize=0)
# sc 队列
scQue = PriorityQueue(maxsize=0)
# 舰长队列
guardQue = PriorityQueue(maxsize=0)
# 礼物
giftQue = PriorityQueue(maxsize=5)
# 普通弹幕队列
danmuQue = PriorityQueue(maxsize=10)

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
        print(f'========\ntype:{type(message)} \n\n')

        for t in trigger.chain:
            print(f'chain:{type(trigger.chain)}, {trigger.chain}')
            print(f't:{t}')
            print(f't.trie:{t.trie}')
            
            for service_func in t.find_handler(message):
                """
                if service_func.only_to_me and not event['to_me']:
                    continue  # not to me, ignore.
                """

                print(f'service_func = {service_func.__name__}')

                service_func.sv.logger.info(f'Message {message.msg} triggered {service_func.__name__}.')
                try:
                    await service_func.func(message)
                except SwitchException:     # the func says: continue to trigger another function.
                    continue
                except CanceledException:   # the func says: stop triggering.
                    raise
                except Exception as e:      # other general errors.
                    service_func.sv.logger.error(f'{type(e)} occured when {service_func.__name__} handling message {message.msg}.')
                    service_func.sv.logger.exception(e)
                # the func completed successfully, stop triggering. (1 message for 1 function at most.)
                raise CanceledException('Handled by Hoshino')
                # exception raised, no need for break

        # 没匹配到命令的消息放进danmuQue，给gpt处理
        if message.dm_type == 0:
            print(f'弹幕：[{client.room_id}] {message.uname}：{message.msg}')
            # 权重计算
            guardLevel = message.privilege_type
            if guardLevel == 0:
                guardLevel = 0
            elif guardLevel == 3:
                guardLevel = 200
            elif guardLevel == 2:
                guardLevel = 2000
            elif guardLevel == 1:
                guardLevel = 20000
            # 舰长权重，勋章id权重*100，lv权重*100
            medalevel = 0
            if message.medal_room_id == roomID:
                medalevel = message.medal_level * 100
            rank = (999999 - message.user_level * 100 -
                    guardLevel - medalevel - message.user_level * 10 + random.random())
            if danmuQue.full():
                try:
                    danmuQue.get(True, 1)
                except BaseException:
                    print("on_danmuku时，get异常")

            queData = {'name': message.uname, 'type': 'danmu', 'num': 1, 'action': '说',
                       'msg': message.msg.replace('[', '').replace(']', ''), 'price': 0}
            # if main_config['env'] == 'dev':
            if True:
                print("当前弹幕队列容量：" + str(danmuQue.qsize()))
                print("rank:" + str(rank) + ";name:" + message.uname + ";msg:" +
                      message.msg.replace('[', '').replace(']', ''))
                print(queData)
            try:
                danmuQue.put((rank, queData), True, 2)
            except Exception as e:
                print("ErrorStart-------------------------")
                print(e)
                print("put弹幕队列异常")
                print(queData)
                print("错误" + str(danmuQue.full()))
                print("错误" + str(danmuQue.empty()))
                print("后弹幕队列容量：" + str(danmuQue.qsize()))
                print("ErrorEnd-------------------------")


        # 如果没匹配到对应的命令，则发送给gpt
        # 测试中，所有消息都发送
        """url = "https://api.dify.ai/v1/chat-messages"
        API_KEY = "app-iiD3gZUiG7SNa6L6oBxTndZc"
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
            'Accept - Encoding': 'utf-8'
        }
        data = {
            "inputs": {},
            "query": f"{message.msg}",
            "response_mode": "blocking",  # blocking, streaming
            "conversation_id": "",
            "user": f"{message.uid}"
        }
        response = requests.post(url, headers=headers, json=data)
        print("====== dify: =====", type(response.text))
        print(response.text)
        resp = json.loads(response.text)
        print(resp)
        answer = resp["answer"]"""



    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        if message.coin_type == 'gold':
            print(f'礼物：：[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
                  f' （{message.coin_type}瓜子x{message.total_coin}）')
            price = message.total_coin / 1000
            if giftQue.full():
                giftQue.get(False, 1)
            if price > 1:
                resp = f"感谢{message.uname}赠送的{message.num} 个{message.gift_name} "
                queData = {"name": message.uname, "type": 'gift', 'num': message.num,
                           'action': message.action, 'msg': resp, 'price': price}
                giftQue.put(
                    (999999 - price + random.random(), queData), True, 1)

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        print(f'上舰：：[{client.room_id}] {message.username} 购买{message.gift_name}')
        resp = f"感谢{message.uname}的舰长"
        queData = {"name": message.username, "type": 'guard', 'num': 1,
                   'action': '上', 'msg': resp, 'price': message.price / 1000}
        guardQue.put((message.guard_level + random.random(), queData))

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        print(f'SC：：[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')
        # 名称、类型、数量、动作、消息、价格
        queData = {"name": message.uname, "type": 'sc', 'num': 1,
                   'action': '发送', 'msg': message.message, 'price': message.price}
        scQue.put((999999 - message.price + random.random(), queData))
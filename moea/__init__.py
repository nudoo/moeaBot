from moea.blivedm import blivedm
from moea.handler import MyHandler
import asyncio
import _thread
from moea import service, tts
from queue import Queue, PriorityQueue
import multiprocessing

class MoeaBot(object):
    def __init__(self, config_object=None):
        """
        You should NOT instantiate a MoeaBot!
        This is for intellisense code completion.
        Use `hoshino.init()` instead.
        """
        super().__init__()

        config_dict = {
            k: v
            for k, v in config_object.__dict__.items()
            if k.isupper() and not k.startswith('_')
        }
        self.room_ids = config_dict["ROOM_IDS"]
        self.is_run = True
        self.tts_queue = multiprocessing.Queue(maxsize=10)
        self.wav_queue = multiprocessing.Queue(maxsize=10)
        self.curr_txt = ""
        # raise Exception("You should NOT instantiate a HoshinoBot! Use `hoshino.init()` instead.")

    async def listener(self):
        """
        同时监听多个直播间
        """
        print(f"by moea: this func is listener")
        clients = [blivedm.BLiveClient(room_id) for room_id in self.room_ids]
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


    async def responder(self):
        print(f"by moea: this func is responder")
        await tts.chatgpt(self.is_run, self.tts_queue)

    async def inference(self):
        await tts.inference(self.is_run, self.tts_queue, self.wav_queue)


    async def play(self):
        await tts.play(self.is_run, self.wav_queue, self.curr_txt)
        """i = 1
        while True:
            print(f"this func is play, i = {i}")
            i += 1
            text = self.wav_queue.get()
            await asyncio.sleep(5)"""

    def run(self):
        # coroutine = self.listener()
        # asyncio.run(coroutine)
        # _thread.start_new_thread(asyncio.run, (self.listener(),))
        # _thread.start_new_thread(asyncio.run, (self.responder(),))
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.create_task(self.listener())
        print("=======listener started")

        loop.create_task(self.responder())
        print("=======responder started")

        loop.run_in_executor(None, self.play)
        print("=======play started")

        loop.run_in_executor(None, self.inference)
        print("=======inference started")

    async def run_async(self):
        await asyncio.gather(self.listener(), self.responder(), self.inference(), self.play())


from . import log, config

_bot = None
logger = log.new_logger('hoshino', config.DEBUG)


def init() -> MoeaBot:
    global _bot
    _bot = MoeaBot(config)
    return _bot

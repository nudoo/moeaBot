import random
import subprocess
import multiprocessing
import pygame
import os
import uuid
import time
import asyncio
import datetime
import requests
import json
from pypinyin import lazy_pinyin
from moea.handler import topQue, scQue, guardQue, giftQue, danmuQue
from moea import config


texts = ["hello world!", "nice to meet you!", "i am fine.", "how are you?", "good night"]
def generated_speech(text, path, audio_name):
    audio = os.path.join(path, audio_name)
    # 生成TTS语音
    command = f'edge-tts --voice zh-CN-XiaoyiNeural --text "{text}" --write-media {audio}.mp3'  # 将 AI 生成的文本传递给 edge-tts 命令
    subprocess.run(command, shell=True)  # 执行命令行指令
    return audio


async def inference(is_run, ttsQue, wav_que):
    print("by moea:运行inference子进程")
    i = 1
    while is_run:
        # 阻塞
        # print(f"by moea: inference")
        text = ""
        if ttsQue.empty():
            await asyncio.sleep(2)
            continue
        else:
            try:
                text = ttsQue.get()
            except Exception as e:
                print("-----------ErrorStart--------------")
                print(e)
                print("gpt获取弹幕异常，当前线程：：")
                print(text)
                print("-----------ErrorEnd--------------")
                await asyncio.sleep(2)
                continue
        path = "output"
        name = str(uuid.uuid1())
        print("生成语音：：" + name + "::" + text)
        generated_speech(text, path, name)
        wav_que.put(name + "::" + text)
        # print(f"by moea: inference, wav_queue深度：{wav_que.qsize()}")
        print(f"this func is inference, i = {i}")
        i += 1
        await asyncio.sleep(1)


def change_txt(txt, curr_txt):
    curr_txt.value = txt


def play_audio(output_path="output", audio_name="audio"):
    audio = os.path.join(output_path, audio_name)
    # 初始化 Pygame
    pygame.mixer.init()

    # 加载语音文件
    audio_file = f"{audio}.mp3"
    print("audio_file is: ", audio_file)
    pygame.mixer.music.load(audio_file)

    # 播放语音
    pygame.mixer.music.play()

    # 等待语音播放结束
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # 退出临时语音文件
    pygame.mixer.quit()


async def play(is_run, wav_que, curr_txt):
    print("by moea:运行play子进程")
    while is_run:
        # 阻塞
        if wav_que.empty():
            print(f"by moea: play: wav_queue is empty")
            await asyncio.sleep(2)
            continue
        print(f"by moea: play, wav_queue深度：{wav_que.qsize()}")
        text = wav_que.get()
        print("开始播放内容::" + text)
        name = text.split("::")[0]
        txt = text.split("::")[1]
        curr_txt = txt

        play_audio(audio_name=name)
        await asyncio.sleep(1)
        """p = multiprocessing.Process(
            target=change_txt, args=(txt, curr_txt))
        p.start()
        play_audio(audio_name=name)
        time.sleep(0.5)
        p.join()"""


# 敏感词
sensitive_txt = 'moea/config/sensitive_words.txt'
sensitiveF = open(sensitive_txt, 'r', encoding='utf-8')
hanzi_sensitive_word = sensitiveF.readlines()
pinyin_sensitive_word = []
for i in range(len(hanzi_sensitive_word)):
    hanzi_sensitive_word[i] = hanzi_sensitive_word[i].replace('\n', '')
    pinyin_sensitive_word.append(str.join('', lazy_pinyin(hanzi_sensitive_word[i])))

# 敏感词音检测
def filter_text(text):
    # 为上舰时直接过
    if text == '-1':
        return True
    textPY = str.join('', lazy_pinyin(text))
    for i in range(len(hanzi_sensitive_word)):
        if hanzi_sensitive_word[i] in text or pinyin_sensitive_word[i] in textPY:
            return False
    return True


async def chatgpt(is_run, tts_que):
    print("运行gpt循环任务")
    while is_run:
        chatObj = {"name": '', "type": '', 'num': 0,
                   'action': '', 'msg': '', 'price': 0}
        # 从队列获取信息
        try:
            if topQue.empty() == False:
                chatObj = topQue.get(True, 1)
            elif guardQue.empty() == False:
                chatObj = guardQue.get(True, 1)
                chatObj = chatObj[1]
            elif giftQue.empty() == False:
                chatObj = giftQue.get(True, 1)
                chatObj = chatObj[1]
            elif scQue.empty() == False:
                chatObj = scQue.get(True, 1)
                chatObj = chatObj[1]
            elif danmuQue.empty() == False:
                chatObj = danmuQue.get(True, 1)
                chatObj = chatObj[1]
        except Exception as e:
            print("-----------ErrorStart--------------")
            print(e)
            print("gpt获取弹幕异常，当前线程：：")
            print(chatObj)
            print("-----------ErrorEnd--------------")
            await asyncio.sleep(2)
            continue

        # print(chatObj)
        # 过滤队列
        if len(chatObj['name']) > 0:
            if filter_text(chatObj['name']) and filter_text(chatObj['msg']):
                send2gpt(chatObj, tts_que)
        else:
            await asyncio.sleep(1)


temp_message = []
def send2gpt(msg, tts_que):
    # 向 gpt 发送的消息
    send_gpt_msg = ''
    # 向 tts 写入的数据
    send_vits_msg = ''
    if msg['type'] == 'danmu':
        # send_gpt_msg = msg['name'] + msg['action'] + msg['msg']
        send_gpt_msg = msg['msg']
        send_vits_msg = msg['msg']
    elif msg['type'] == 'sc':
        send_gpt_msg = msg['name'] + msg['action'] + \
                       str(msg['price']) + '块钱sc说' + msg['msg']
        send_vits_msg = send_gpt_msg
    elif msg['type'] == 'guard':
        guardType = '舰长'
        if msg['price'] > 200:
            guardType = '提督'
        elif msg['price'] > 2000:
            guardType = '总督'
        send_gpt_msg = msg['name'] + msg['action'] + \
                       guardType + '了,花了' + str(msg['price']) + '元'
        send_vits_msg = msg['name'] + msg['action'] + guardType + '了'
    elif msg['type'] == 'gift':
        send_gpt_msg = msg['name'] + msg['action'] + msg['msg']
        send_vits_msg = send_gpt_msg
    else:
        send_gpt_msg = msg['msg']
        send_vits_msg = send_gpt_msg

    # 生成上下文
    temp_message.append({"role": "user", "content": send_gpt_msg})
    # 上下文最大值
    if len(temp_message) > 3:
        del (temp_message[0])
    message = temp_message

    # 子进程4
    # 开启 openai 进程
    if tts_que.full() == False:
        p = multiprocessing.Process(target=rec2tts, args=(
            msg, send_gpt_msg, message, send_vits_msg, tts_que))
        p.start()
        # join 会阻塞当前 gpt 循环线程，但不会阻塞弹幕线程
        print("openai请求子进程开启完成")
        if tts_que.full():
            p.join()


def rec2tts(msg, send_gpt_msg, message, send_vits_msg, tts_que):
    print("进入openai chatgpt进程，向gpt发送::" + send_gpt_msg)

    url = "https://api.dify.ai/v1/chat-messages"
    API_KEY = config.API_KEY
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
        'Accept - Encoding': 'utf-8'
    }
    data = {
        "inputs": {},
        "query": f"{send_gpt_msg}",
        "response_mode": "blocking",  # blocking, streaming
        "conversation_id": "",
        "user": f"{msg['name']}"
    }
    response = requests.post(url, headers=headers, json=data)
    print("====== dify: =====", type(response.text))
    print(response.text)
    resp = json.loads(response.text)
    print(resp)
    answer = resp["answer"]

    # 敏感词词音过滤
    if filter_text(answer) == False:
        print("检测到敏感词内容::" + answer)
        return
    print("从gpt接收::" + answer)
    # tts_que.put(send_vits_msg)
    tts_que.put(answer)

# tts
# tts_que = multiprocessing.Queue(maxsize=int(tts_config['max_wav_queue']))
# wav_que = multiprocessing.Queue(maxsize=int(tts_config['max_wav_queue']))
tts_que = multiprocessing.Queue(maxsize=int(config.max_wav_queue))
wav_que = multiprocessing.Queue(maxsize=int(config.max_text_length))

"""async def play_audio(content: str, output_path="output", audio_name="audio"):
    audio = os.path.join(output_path, audio_name)
    #生成TTS语音
    command = f'edge-tts --voice zh-CN-XiaoyiNeural --text "{content}" --write-media {audio}.mp3'  # 将 AI 生成的文本传递给 edge-tts 命令
    subprocess.run(command, shell=True)  # 执行命令行指令
    # 初始化 Pygame
    pygame.mixer.init()

    # 加载语音文件
    pygame.mixer.music.load(f"{audio}.mp3")

    # 播放语音
    pygame.mixer.music.play()

    # 等待语音播放结束
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # 退出临时语音文件
    pygame.mixer.quit()"""
if __name__ == "__main__":
    text = "人生何处不相逢，相逢何必是梦中。梦中应识归来路，路上相逢无纸笔。笔落惊风雨，雨打风吹雪。"
    audio = generated_speech(text, "./", "life")
    play_audio("", audio)

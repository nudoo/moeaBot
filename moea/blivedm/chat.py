

def on_chat(client, message):
    msg = message.msg
    res = deal_msg(msg)


def deal_msg(msg:str):

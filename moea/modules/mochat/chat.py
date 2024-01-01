from moea import service

sv = service.Service('chat')

@sv.on_prefix('查询')
async def say_query(message):
    print(f'查询：{message.uname} {message.msg}')
    sv.logger.info(f'查询： {message.uname} {message.msg} triggered {sv.name}.')


@sv.on_prefix('check')
async def say_check(message):
    print(f'check: {message.uname} {message.msg}')

@sv.on_prefix('早上好')
async def say_hello(message):
    print(f'打招呼：{message.uname} {message.msg}')
    sv.logger.info(f'打招呼： {message.uname} {message.msg} triggered {sv.name}.')



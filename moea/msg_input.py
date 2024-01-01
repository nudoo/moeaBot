from trigger import prefix, CQEvent


def main():
    print(prefix.trie.keys())

    data = input('请输入data：')
    message = list()
    msg = dict()
    msg['type'] = 'text'
    msg['data'] = data
    print(msg)
    message.append(msg)
    event = CQEvent()
    event.__setattr__('user_id', 999)
    event.__setattr__('message', message)
    for service_func in prefix.find_handler(event):
        print(service_func)


if __name__ == "__main__":
    main()


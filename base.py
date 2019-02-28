from aria2 import *
# SERVER_URL = 'http://192.168.2.100:6800/jsonrpc'
SERVER_URL = 'http://118.25.17.65:6800/jsonrpc'


if __name__ == '__main__':
    aria2 = Aria2(SERVER_URL, 'allan')
    # ret = aria2.list_methods()
    # print(json.dumps(ret, indent=4))

    ret = aria2.get_system_status()
    print(json.dumps(ret, indent=4))

    # ret = aria2.get_version()
    # print(json.dumps(ret, indent=4))
    ret = aria2.get_stopped_tasks()
    print(len(ret['result']))
    # print(json.dumps(ret, indent=4))
    ret = aria2.get_waiting_tasks()
    print(len(ret['result']))
    # print(json.dumps(ret, indent=4))
    ret = aria2.get_active_tasks()
    print(len(ret['result']))
    # print(json.dumps(ret, indent=4))

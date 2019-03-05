from aria2 import *
# SERVER_URL = 'http://192.168.2.100:6800/jsonrpc'
#SERVER_URL = 'http://118.25.17.65:6800/jsonrpc'
SERVER_URL = 'http://127.0.0.1:6800/jsonrpc'


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
    if len(ret['result']) > 0:
        open('doc/stopped.json', 'w+').write(json.dumps(ret['result'], indent=4))
    # print(json.dumps(ret, indent=4))
    ret = aria2.get_waiting_tasks()
    print(len(ret['result']))
    if len(ret['result']) > 0:
        open('doc/waiting.json', 'w+').write(json.dumps(ret['result'], indent=4))
    # print(json.dumps(ret, indent=4))
    # ret = aria2.get_peers('3285cbc5437a7333')
    print(json.dumps(ret['result'], indent=4))
    ret = aria2.get_active_tasks()
    print(len(ret['result']))
    if len(ret['result']) > 0:
        open('doc/active.json', 'w+').write(json.dumps(ret['result'], indent=4))
    for task in ret['result']:
        if 'numSeeders' in task and int(task['numSeeders']) > 0:
            peers = aria2.get_peers(task['gid'])
            open('doc/peers.json', 'w+').write(json.dumps(peers['result'], indent=4))
    # print(json.dumps(ret, indent=4))

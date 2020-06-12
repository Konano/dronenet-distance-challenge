import requests
import re
import json
import time
import numpy as np
from queue import Queue
from threading import Thread, Lock

proxies = {
    'http': "http://127.0.0.1:1881",
    'https': "http://127.0.0.1:1881",
}


def fetchPortals(nelat, nelng, swlat, swlng, offset):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
    url = f'https://lanched.ru/PortalGet/getPortals.php'
    params = {'nelat': nelat, 'nelng': nelng, 'swlat': swlat, 'swlng': swlng, 'offset': offset}
    while True:
        try:
            ret = requests.get(url=url, params=params, headers=headers, timeout=(5, 10), proxies=proxies)
        except:
            print('error in', nelat, nelng, swlat, swlng, offset)
            continue
        return ret.json()


def getPortals(nelat, nelng, swlat, swlng):
    ret = fetchPortals(nelat, nelng, swlat, swlng, 0)
    portals = ret['portalData']
    while ret['nextOffset'] != -1:
        ret = fetchPortals(nelat, nelng, swlat, swlng, ret['nextOffset'])
        portals += ret['portalData']
    return portals


class TaskQueue(Queue):
    def __init__(self, num_workers=1):
        Queue.__init__(self)
        self.num_workers = num_workers
        self.start_workers()

    def start_workers(self):
        for _ in range(self.num_workers):
            t = Thread(target=self.do_task)
            t.daemon = True
            t.start()

    def add_task(self, func, *args, **kwargs):
        args = args or ()
        kwargs = kwargs or {}
        self.put((func, args, kwargs))

    def do_task(self):
        while True:
            func, args, kwargs = self.get()
            func(*args, **kwargs)
            self.task_done()

q = TaskQueue(num_workers=10)




total = 0
if __name__ == '__main__': # All

    lock = Lock()

    def subtask(lock, x, y):
        ret = getPortals(x, y, x-10, y-10)
        lock.acquire()
        global total
        total += len(ret)
        np.save(f"data_raw/{x}_{y}.npy", ret)
        print(f'{total/11500633*100:05.2f}%, x: {x}, y: {y}, total: {len(ret)}, now: {total}/{11500633}')
        lock.release()

    for x in range(90, -90, -10):
        for y in range(180, -180, -10):
            q.add_task(subtask, lock, x, y)

    q.join()
    print('Task all done')
    print(f'Portal Total: {total}')



# if __name__ == '__main__': # Single

#     def subtask(lock, x, y, offset, portals):
#         ret = fetchPortals(x, y, x-10, y-10, offset)
#         lock.acquire()
#         global total
#         total += len(ret['portalData'])
#         portals += ret['portalData']
#         print(f'{total/11500633*100:05.2f}%, x: {x}, y: {y}, total: {len(portals)}, now: {total}/{11500633}')
#         lock.release()

#     def quest(x, y, o):
#         lock = Lock()
#         portals = []
#         for offset in range(0, o, 1000):
#             q.add_task(subtask, lock, x, y, offset, portals)
#         q.join()
#         np.save(f"data_raw/{x}_{y}.npy", portals)

#     quest(40, 140, 1000000)
#     quest(-20, -40, 400000)

#     print('Task all done')
#     print(f'Portal Total: {total}')

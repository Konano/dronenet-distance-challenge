from s2sphere import Cap, LatLng, RegionCoverer, Cell, CellId
import math
import numpy as np
import os
import progressbar
from multiprocessing import Pool, Queue, Manager
import threading
import time

PORTAL_NUM = 11475124
MAX_S2_CELLS = 1000
earthCircumferenceMeters = 1000 * 40075.017

def earthMetersToRadians(meters):
    return (2 * math.pi) * (float(meters) / earthCircumferenceMeters)

def getCoveringRect(lat, lng, radius):
    radius_radians = earthMetersToRadians(radius)
    latlng = LatLng.from_degrees(float(lat), 
             float(lng)).normalized().to_point()
    region = Cap.from_axis_height(latlng, 
    (radius_radians*radius_radians)/2)
    coverer = RegionCoverer()
    coverer.min_level = 1
    coverer.max_level = 16
    coverer.max_cells = MAX_S2_CELLS
    covering = coverer.get_covering(region)
    return covering

def special_getCoveringRect(lat, lng, radius):
    radius_radians = earthMetersToRadians(radius)
    latlng = LatLng.from_degrees(float(lat), 
             float(lng)).normalized().to_point()
    region = Cap.from_axis_height(latlng, 
    (radius_radians*radius_radians)/2)
    coverer = RegionCoverer()
    coverer.min_level = 5
    coverer.max_level = 5
    coverer.max_cells = MAX_S2_CELLS
    covering = coverer.get_covering(region)
    return covering

def getPortals(cell):
    ret = []
    try:
        for p in np.load(f"data/{cell.parent(5).to_token()}/{cell.parent(10).to_token()}.npy"):
            if cell.contains(CellId.from_token(p['cellid'])):
                ret.append(p)
    except:
        pass
    return ret

def subtask(filename, t, h):
    parent = CellId.from_token(filename[:-4])
    data = np.load(f'data_fc/{filename}')
    lv16 = {}
    lv15 = {}
    lv14 = {}
    head = {}
    for i in range(len(data)):
        head[data[i]['id']] = data[i]['id']

    def find(x):
        if head[head[x]] != head[x]:
            head[x] = find(head[x])
        return head[x]

    for i in range(len(data)):
        cell_id = CellId.from_token(data[i]['cellid'])

        p_16 = cell_id.parent(16).to_token()
        if p_16 not in lv16.keys():
            lv16[p_16] = []
        lv16[p_16].append(data[i])

        p_15 = cell_id.parent(15).to_token()
        if p_15 not in lv15.keys():
            lv15[p_15] = []
        lv15[p_15].append(data[i])

        p_14 = cell_id.parent(14).to_token()
        if p_14 not in lv14.keys():
            lv14[p_14] = []
        lv14[p_14].append(data[i])

    for i in range(len(data)):
        cells = getCoveringRect(data[i]['lat'], data[i]['lng'], 500)
        H = find(data[i]['id'])
        for cell in cells:
            if parent.contains(cell) == False:
                for pp in getPortals(cell):
                    if pp['id'] != data[i]['id']:
                        h.put((pp['id'], data[i]['id']))
            elif cell.level() == 16:
                if cell.to_token() in lv16.keys():
                    for pp in lv16[cell.to_token()]:
                        if pp['id'] != data[i]['id']:
                            head[find(pp['id'])] = H
            elif cell.level() == 15:
                if cell.to_token() in lv15.keys():
                    for pp in lv15[cell.to_token()]:
                        if pp['id'] != data[i]['id']:
                            head[find(pp['id'])] = H
            elif cell.level() == 14:
                if cell.to_token() in lv14.keys():
                    for pp in lv14[cell.to_token()]:
                        if pp['id'] != data[i]['id']:
                            head[find(pp['id'])] = H
        total = t.get(True)
        t.put(total+1)

    for key, value in head.items():
        h.put((key, value))


if __name__ == '__main__':

    files = os.listdir('data_fc/')
    
    p = progressbar.ProgressBar()
    p.start(PORTAL_NUM)
    total = 0

    # init head
    # head = np.arange(0, PORTAL_NUM, 1)
    # np.save('head.npy', head)

    head = np.load('head.npy')

    def find(x):
        if head[head[x]] != head[x]:
            head[x] = find(head[x])
        return head[x]

    manager = Manager()
    t = manager.Queue()
    t.put(0)
    h = manager.Queue()

    pl = Pool(12)
    for filename in os.listdir('data_fc/'):
        pl.apply_async(subtask, args=(filename, t, h,))
    pl.close()
    
    def run_total():
        global total, t
        while total != PORTAL_NUM:
            try:
                total = t.get(True, timeout=10)
                t.put(total)
                p.update(total)
                if total == PORTAL_NUM:
                    p.finish()
                    return
            except:
                print('run_total ERROR')
                pass
        time.sleep(0.1)

    def run_head():
        global total, h
        while total != PORTAL_NUM:
            try:
                x, y = h.get(True, timeout=10)
                head[find(x)] = find(y)
            except:
                np.save('head.npy', head)
                print('\nsave head.npy')
                pass

    t1 = threading.Thread(target=run_total, args=())
    t2 = threading.Thread(target=run_head, args=())
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    pl.join()

    np.save('head.npy', head)

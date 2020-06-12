import numpy as np
import math
import progressbar
from s2sphere import LatLng, CellId
import os

PORTAL_NUM = 11475124

if __name__ == '__main__':

    p = progressbar.ProgressBar()

    # data_raw -> data_fc
    p.start(PORTAL_NUM)
    total = 0

    for x in range(90, -90, -10):
        for y in range(180, -180, -10):
            data = np.load(f"data_raw/{x}_{y}.npy")
            areas = {}
            for i in range(len(data)):
                cell_id = CellId.from_lat_lng(LatLng.from_degrees(float(data[i]['lat']), float(data[i]['lng'])))
                parent = cell_id.parent(5).to_token()
                if parent not in areas.keys():
                    if os.path.exists(f"data_fc/{parent}.npy"):
                        areas[parent] = list(np.load(f"data_fc/{parent}.npy"))
                    else:
                        areas[parent] = []
                data[i]['cellid'] = cell_id.to_token()
                data[i]['id'] = total
                areas[parent].append(data[i])
                total += 1
                p.update(total)
            for key, value in areas.items():
                np.save(f"data_fc/{key}.npy", value)

    p.finish()


    # data_fc -> data
    p.start(PORTAL_NUM)
    total = 0

    for filename in os.listdir('data_fc/'):
        data = np.load(f'data_fc/{filename}')
        areas = {}
        for i in range(len(data)):
            cell_id = CellId.from_token(data[i]['cellid'])
            parent = cell_id.parent(10).to_token()
            if parent not in areas.keys():
                areas[parent] = []
            areas[parent].append(data[i])
            total += 1
            p.update(total)
        os.makedirs(f"data/{filename[:-4]}")
        for key, value in areas.items():
            np.save(f"data/{filename[:-4]}/{key}.npy", value)
    p.finish()
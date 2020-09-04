import numpy as np
import os, sys
import convex
import geo
from s2sphere import Cap, LatLng, RegionCoverer, Cell, CellId
import json
import math

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

portals = np.array([])
lv16 = {}
lv15 = {}
lv14 = {}
lv10 = []
pos = {}

def load(cell_id):

    if cell_id.parent(10).to_token() in lv10:
        return

    try:
        data = np.load(f"data/{cell_id.parent(5).to_token()}/{cell_id.parent(10).to_token()}.npy")
    except:
        return
    lv10.append(cell_id.parent(10).to_token())

    for i in range(len(data)):
        pos[data[i]['cellid']] = (data[i]['lat'], data[i]['lng'])
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

    global portals
    portals = np.concatenate((portals, data))

def path(start_lat, start_lng):

    cell_id = CellId.from_lat_lng(LatLng.from_degrees(float(start_lat), float(start_lng)))
    token = cell_id.to_token()
    jump = {}
    jump[token] = {'layer': 0, 'pre': ''}
    queue = [token]

    total = 0
    start = token

    mxdis = 0
    mxpor = None
    prelayer = -1

    while len(queue) > 0:
        total += 1
        token = queue[0]
        queue = queue[1:]
        cell_id = CellId.from_token(token)
        load(cell_id)

        if jump[token]['layer'] != prelayer:
            prelayer = jump[token]['layer']
            print(jump[token]['layer'], total, mxdis)

        if geo.haversine(pos[start], pos[token]) > mxdis:
            mxdis = geo.haversine(pos[start], pos[token])
            mxpor = token

        cells = getCoveringRect(pos[token][0], pos[token][1], 500)
        for cell in cells:
            load(cell)
            if cell.level() == 16:
                if cell.to_token() in lv16.keys():
                    for pp in lv16[cell.to_token()]:
                        if pp['cellid'] not in jump.keys():
                            jump[pp['cellid']] = {'layer': jump[token]['layer']+1, 'pre': token}
                            queue.append(pp['cellid'])
            elif cell.level() == 15:
                if cell.to_token() in lv15.keys():
                    for pp in lv15[cell.to_token()]:
                        if pp['cellid'] not in jump.keys():
                            jump[pp['cellid']] = {'layer': jump[token]['layer']+1, 'pre': token}
                            queue.append(pp['cellid'])
            elif cell.level() == 14:
                if cell.to_token() in lv14.keys():
                    for pp in lv14[cell.to_token()]:
                        if pp['cellid'] not in jump.keys():
                            jump[pp['cellid']] = {'layer': jump[token]['layer']+1, 'pre': token}
                            queue.append(pp['cellid'])

    print(mxdis)
    token = mxpor
    draw = [{"type": "polyline", "latLngs": [{"lat": pos[token][0], "lng": pos[token][1]}], "color": "#a24ac3"}]
    while jump[token]['layer'] > 0:
        token = jump[token]['pre']
        draw.append({"type": "circle", "latLng": {"lat": pos[token][0], "lng": pos[token][1]}, "radius": 500, "color":"#a24ac3"})
        draw[0]['latLngs'].append({"lat": pos[token][0], "lng": pos[token][1]})

    with open(f'path_{start_lat}_{start_lng}.json', 'w') as f:
        json.dump(draw, f)


if __name__ == "__main__":
    path(float(sys.argv[1]), float(sys.argv[2]))

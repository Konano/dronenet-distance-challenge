import numpy as np
import progressbar, os
import convex
import geo
import json

PORTAL_NUM = 11475124

# ret = np.load("result.npz")

# head = ret['arr_0']
# count = ret['arr_1']
# grp = ret['arr_2']



# collect = []
# for i in range(np.max(grp)+1):
#     collect.append([])

# pb = progressbar.ProgressBar()
# pb.start(PORTAL_NUM)
# total = 0
# for filename in os.listdir('data_fc/'):
#     data = np.load(f'data_fc/{filename}')
#     for p in data:
#         collect[grp[head[p['id']]]].append([p['lat'],p['lng']])
#         total += 1
#         pb.update(total)
# pb.finish()

# np.save("collect.npy", collect)
collect = np.load("collect.npy")


# def graham_scan(points):
#     while len(points) >= 1000:
#         points = points[:-1000] + convex.graham_scan(points[-1000:])
#     return convex.graham_scan(points)


# def faraway(points):
#     if len(points) > 100:
#         print('\n', len(points))
#     dis = 0
#     for i in range(len(points)):
#         for j in range(i+1,len(points)):
#             dis = max(dis, geo.haversine(points[i], points[j]))
#     return dis

# far = []
# pb = progressbar.ProgressBar()
# pb.start(len(collect))
# for i in range(len(collect)):
#     # if len(collect[i]) > 1000:
#     #     print('\n', len(collect[i]))
#     collect[i] = graham_scan(collect[i])
#     far.append((faraway(collect[i]), i))
#     pb.update(i+1)
# pb.finish()
# np.save("convex.npy", collect)

# far.sort(reverse=True)
# np.save("far.npy", far)


collect = np.load("convex.npy")
far = np.load("far.npy")

# china = [
#     [26.54922257769204, 49.75287993415023, 73.6083984375, 102.041015625],
#     [17.22475820662464, 53.461890432859114, 97.3828125, 123.96972656249999],
#     [38.85682013474361, 53.72271667491848, 114.60937499999999, 135.3955078125]
# ]

# mnlat = 18.60460138845525
# mxlat = 43.197167282501276
# mnlng = 97.91015624999999
# mxlng = 124.01367187499999

# for i in range(100):
#     with open(f'result/{i}.json', 'w') as f:
#         json.dump([{"type": "marker", "latLng": {"lat": x[0], "lng": x[1]}, "color": "#a24ac3"} for x in collect[int(far[i][1])]], f)
#     print(i, far[i][0])

def random_bits(len):
    assert len % 8 == 0
    len //= 8
    n = os.urandom(len)
    while n[0] & 1 == 0 or n[-1] & 0x80 == 0:
        n = os.urandom(len)
    return n

# with open(f'result/Top100.json', 'w') as f:
#     all = []
#     for i in range(100):
#         color = f'#{random_bits(24).hex()}'
#         all += [{"type": "marker", "latLng": {"lat": x[0], "lng": x[1]}, "color": color} for x in collect[int(far[i][1])]]
#         print(i, color, far[i][0])
#     json.dump(all, f)

with open(f'result/TopChina.json', 'w') as f:
    all = []
    for i in range(2000):
        for j in range(3):
            if china[j][0] <= collect[int(far[i][1])][0][0] and \
               collect[int(far[i][1])][0][0] <= china[j][1] and \
               china[j][2] <= collect[int(far[i][1])][0][1] and \
               collect[int(far[i][1])][0][1] <= china[j][3]:
                color = f'#{random_bits(24).hex()}'
                all += [{"type": "marker", "latLng": {"lat": x[0], "lng": x[1]}, "color": color} for x in collect[int(far[i][1])]]
                print(i, color, far[i][0])
                break
    json.dump(all, f)
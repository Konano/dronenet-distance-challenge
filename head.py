import numpy as np
import progressbar, os

PORTAL_NUM = 11475124
    
pb = progressbar.ProgressBar()

head = np.load('head.npy')

def find(x):
    if head[head[x]] != head[x]:
        head[x] = find(head[x])
    return head[x]

num = len(head)
count = np.zeros_like(head)
grp = np.zeros_like(head)

total = 0

pb.start(PORTAL_NUM)
for i in range(num):
    count[find(i)] += 1
    pb.update(i+1)
    if head[i] == i:
        grp[i] = total
        total += 1
pb.finish()

np.savez("result.npz", head, count, grp)

print(np.max(count))
print(total)

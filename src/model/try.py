
dist = {}

dist[1] = 10
dist[2] = 1
dist[3] = 4
dist[4] = 2
dist[5] = 5
print(dist)
sorted_dist = sorted(dist.items(), key=lambda kv: kv[1])
# print(sorted_dist)
# sorted_dist_dict = dict(sorted_dist)
j = sorted_dist[:4]
keys = [pair[0] for pair in j]
print(j)
print(keys)
[{1: 10, 2: 12, 3:10}, {1: 10, 2: 12}]
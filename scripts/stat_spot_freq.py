import csv
import collections

data_path = '/home/01052711/kankan/dataset/jalan_kanko.csv.tokyo.csv'

ctr = collections.defaultdict(int)
with open(data_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        ctr[row['name']] += 1

for name, cnt in sorted(ctr.items(), key=lambda x: x[1], reverse=True):
    print(name + '\t' + str(cnt))
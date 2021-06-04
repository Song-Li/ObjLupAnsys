import os

res = []
with open("from.list", 'r') as fp:
    for line in fp.readlines():
        line = line.strip()
        res.append(os.path.basename(line))

with open("to.list", 'w') as fp:
    fp.write('\n'.join(res))

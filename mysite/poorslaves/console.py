import sqlite3
import json


DB=r'C:\Users\andy\Downloads\db (1).sqlite3'

conn = sqlite3.connect(DB)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master where name like 'poorslaves_%'")
print(cursor.fetchall())
yrs = {}
all = cursor.execute('select * from poorslaves_document').fetchall()

for a in all:
    p = json.loads(a[5])
    c = p['case_id']
    yr = c.split(" ")[1].split("/")[1]
    c = yrs.get(yr, 0)
    yrs[yr] = c+1
items = list(yrs.items())
items.sort(key = lambda x: x[0])
total = 0
for k, v in items:
    total += v
    print(f'{k}\t{v}')
print(f'Total: {total}')
us = {}
ds = {}
uds = {}
all = cursor.execute('select * from poorslaves_answer').fetchall()
for a in all:
    j = json.loads(a[1])
    m = j['meta']
    u = m['username']
    d = m['time'].split(" ")[0]
    c =  us.get(u, 0)
    us[u] = c+1
    c =  ds.get(d, 0)
    ds[d] = c+1
    ud = '%s-%s' % (u, d)
    c = uds.get(ud, 0)
    uds[ud] = c+1
items = list(us.items())
items.sort(key = lambda x: x[1])
total = 0
for k, v in items:
    print(f'{k}\t{v}')
    total += v
print('Total %s' % total)
print()

items = list(ds.items())
items.sort(key = lambda x: x[0])
total = 0
for k, v in items:
    print(f'{k}\t{v}')
    total += v
print(f'Total {total}')
print()

items = list(uds.items())
items.sort(key = lambda x: x[1])
total = 0
i = 0

for k, v in items:
    if v < 10:
        continue
    i += 1
    print(f'{i} {k}\t{v}')
    total += v
print(f'Total {total}, {total/i}')
print()

all = cursor.execute('select * from poorslaves_answer').fetchall()



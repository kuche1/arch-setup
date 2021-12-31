#! /usr/bin/env python3

import psutil

mem = psutil.virtual_memory()

total = mem.total
used_by_user = mem.used
available = mem.available
free = mem.free
used = total - available

r = lambda num: '%.2f'% (num/(1024**3))
total = r(total)
used_by_user = r(used_by_user)
available = r(available)
free = r(free)
used = r(used)

i = ''
#print(f"{i} {r(used_by_user)} | {r(used)} {i} {r(available)} | {r(free)}")
print(f"{i} [={total}|+{available}|-{used}]<{free}|{used_by_user}>")

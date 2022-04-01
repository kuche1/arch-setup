#! /usr/bin/env python3

import psutil

mem = psutil.virtual_memory()

total = mem.total
#used_by_user = mem.used
available = mem.available
#free = mem.free
used = total - available

r = lambda num: '%.2f'% (num/(1024**3))
total = r(total)
#used_by_user = r(used_by_user) # what the user ses as used
available = r(available) # can be used by programs
#free = r(free) # is not used even for caching
used = r(used)

i = ''
#print(f"{i} {available}+{free}|{used}-{used_by_user}|{total}")
print(f"{i} {available}--{used}=={total}")

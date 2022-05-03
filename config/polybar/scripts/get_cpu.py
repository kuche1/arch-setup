#! /usr/bin/env python3

import os
import psutil # pip3 install psutil

_1, _5, _15 = os.getloadavg()
_max = psutil.cpu_count()

fmt = lambda x: f'{x:.2f}'
_1 = fmt(_1)
_5 = fmt(_5)
_15 = fmt(_15)

# 
print(f"[{_1}|{_5}|{_15}|{_max}]")

#! /usr/bin/env python3

import datetime
import time

LIFESPAN = 50 # in years

birth = datetime.datetime(2000, 9, 30).timestamp()
now = time.time()

age = (now - birth) / (60*60*24*365.25)
time_used = (age ** 0.5) / (LIFESPAN ** 0.5)
time_left = 1 - time_used
left = time_left * 100

print(f'{left:.8f}')

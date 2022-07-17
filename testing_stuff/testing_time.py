
import datetime
import time

def clock():
    print("CLOCK")

old_min = None

while True:
    minute = datetime.datetime.now().minute
    if old_min != minute:
        old_min = minute
        clock()
    time.sleep(1)


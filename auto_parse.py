#!/usr/bin/env python3

import schedule
import time
from logparser import main

schedule.every().minute.at(':01').do(main)

while True:
    schedule.run_pending()
    time.sleep(60)

#!/usr/bin/env python3
from logparser import parse_attempts, check_warnings
import time
import re

filepath = '/var/log/auth.log'

def tail_log(filepath):
    with open(filepath) as file:
        file.seek(0, 2)  
        while True:
            line = file.readline()
            if line:
                yield line
            else:
                time.sleep(1) 



def monitor(filepath):
    failed = {}
    accepted = {}
    for line in tail_log(filepath):
        f, a = parse_attempts(line)
        for entry in f:
            ips = re.findall(r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)', entry, re.X)
            if ips:
                ip= ips[0]
                failed[ip] = failed.get(ip, 0) + 1
        for entry in a:
            ips = re.findall(r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)', entry, re.X)
            if ips:
                ip= ips[0]
                accepted[ip] = accepted.get(ip, 0) + 1
        check_warnings(failed, accepted)

monitor(filepath)

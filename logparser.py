#!/usr/bin/env python3
"""
Intro to Python Project
This is a script will open and parse access log files and consolidate data.
The data will be used to identify patterns in login attempts.
Author: NAME_HERE, LaGuardia Community College, MAC 108 sec.3033

*****************************************************************************
|                                                                           |
| TODO:                                                                     |
|                                                                           |
|   [x] def then def main and call each as needed, move top logic to main   |
|   [x] count fails and IPS  -- format into dictionary(?)                   |
|   [1/2] pull/merge machines & sync repo                                   |
|   [ ] Change name before submitting                                       |
|                                                                           |
*****************************************************************************
"""
import re
from datetime import datetime
# ruff: noqa: FURB167

def parse_time(line):
    '''DOCSTRING'''
    time_string = ' '.join(line.split()[:3])
    time_string = f'{datetime.now().year} {time_string}'
    return datetime.strptime(time_string, "%Y %b %d %H:%M:%S")  #noqa
     
def parse_fail_attempts(line):
    auth_failed = []
    failed_attempts = re.search('Failed', line)
    if failed_attempts:
        auth_failed.append(line)
    return auth_failed

def parse_ip(line):
    '''Extract IPs and add to a list'''
    ip_a = []
    for fail in line:
        ip_a += re.findall(r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)', fail, re.X)
    ip_a.sort()
    try:
        counts = {x: ip_a.count(x) for x in set(ip_a)}
    except ValueError:
        counts = None
    return ip_a, counts


# ------------- logic ----------------
def main():
    entries = []  # should I use a dictionary? The world will never know.
    with open('sample_auth.log') as log:
        # CHANGE to '/var/log/auth.log' (/or/other/path) before deployment
        for line in log:
            if "Failed" in line:
                entries.extend(parse_fail_attempts(line))
# how do i sort this in chrono order? (use timestamp) 
    ip_list, ip_dic = parse_ip(entries)
   # ip_count = dict(map(lambda ip, count: (ip, count), )) 
    entries.sort(key=parse_time)
    print(ip_dic)
    print(ip_list)
    for entry in entries:
        print(entry)


if __name__ == "__main__":
    main() 

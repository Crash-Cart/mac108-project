#!/usr/bin/env python3
"""
Intro to Python Project
This is a script will open and parse access log files and consolidate data. 
The data will be used to identify patterns in login attempts.
Author: NAME_HERE, LaGuardia Community College, MAC 108 sec.3033
Sources: claude.ai, https://www.w3schools.com/python/python_regex.asp , https://docs.python.org/3/library/re.html , https://www.w3schools.com/python/python_datetime.asp 
"""


'''
TODO:
     - def then def main and call each as needed, move top logic to main
     - Change name before submitting
     - count fails and IPS  -- format into dictionary(?)
     - pull/merge desktop to sync repo
'''

import re
from datetime import datetime

listed_fails = []
with open('sample_auth.log') as log:  # CHANGE to '/var/log/auth.log' before deployment
    for line in log:
        failed_attempts = re.search('Failed', line)
        if failed_attempts:
            listed_fails.append(line)
        # Parse file for failed login attempts and add to a list.


def parse_time(line):
    time_string = ' '.join(line.split()[:3])
    return datetime.strptime(time_string, "%b %d %H:%M:%S")  #noqa
     


# make this a function and call in larger func, maybe class creation?
def parse_ip():
    pass
ip_a = []
for fail in listed_fails:
    ip_a.append(re.findall(r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)', fail, re.X))  #noqa
    # Add IPs to a list

    '''I had to ask claude for help, specifying not to give the answer:
        
        You're on the right track with the structure — 
        regex for IP addresses is one of those ones that's genuinely tricky to figure out from scratch. 
        Let me give you a hint rather than the answer.
        An IPv4 address is just four groups of numbers separated by dots. 
        Each group is 1-3 digits. In regex:

        \\d{1,3} matches 1 to 3 digits
        \\. matches a literal dot

        So you need four of those groups with dots between them. 
        Give it another shot with that in mind — how would you chain those pieces together?'''

def main():
    pass

if __name__ == "__main__":
    # print fail logs
    print('Fails')
    print(listed_fails)
    print()
    print('Logged IPs')
    # check list of IP addresses
    print(ip_a)
    main() 

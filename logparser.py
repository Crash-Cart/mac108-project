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
|   [ ] Change my name before submitting                                       |
|                                                                           |
*****************************************************************************
"""
import re
from datetime import datetime
import logging

# ruff: noqa: FURB167

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # .disabled = True


def parse_time(line):
    '''DOCSTRING'''
    time_string = ' '.join(line.split()[:3])
    time_string = f'{datetime.now().year} {time_string}'
    return datetime.strptime(time_string, "%Y %b %d %H:%M:%S")  # noqa


def parse_attempts(line):
    auth_failed = []
    auth_accept = []
    if re.search('Failed', line):
        auth_failed.append(line)
    if re.search('Accepted', line):
        auth_accept.append(line)
    return auth_failed, auth_accept


def parse_ip(lines):
    '''Extract IPs from a list of log lines and return (ip_list, {ip: count})'''
    ip_a = []
    for line in lines:
        ip_a += re.findall(r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)', line, re.X)
    ip_a.sort()
    try:
        counts = {x: ip_a.count(x) for x in set(ip_a)}
    except ValueError:
        logging.error('ValueError', exc_info=True)
        counts = None
    return ip_a, counts


def check_warnings(failed_counts, accept_counts):
    '''Warn if an IP has 2 or more failed attempts'''
    for ip, count in failed_counts.items():
        if count >= 2:
            accepted = accept_counts.get(ip, 0)
            print(
                f'WARNING: {ip} has {count} failed attempt(s), {accepted} accepted')


# ------------- logic ----------------
def main():
    auth_failed = []
    auth_accept = []
    with open('sample_auth.log') as log:
        # CHANGE to '/var/log/auth.log' (/or/other/path) before deployment
        for line in log:
            failed, accepted = parse_attempts(line)
            auth_failed.extend(failed)
            auth_accept.extend(accepted)
            logging.debug('sending line to attempt parse')

    _, failed_counts = parse_ip(auth_failed)
    _, accept_counts = parse_ip(auth_accept)
    auth_failed.sort(key=parse_time)
    auth_accept.sort(key=parse_time)

    # testing
    logger.info(f'failed IP counts: {failed_counts}')
    logger.info(f'accepted IP counts: {accept_counts}')

    check_warnings(failed_counts, accept_counts)


if __name__ == "__main__":
    main()

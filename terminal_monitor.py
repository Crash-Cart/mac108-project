'''
This script shall remain open in a terminal window and print log lines as they are generated.

Author: , CUNY LaGuardia Community College, MAC 108 3033, April 17th, 2026
'''
from logparser import parse_time, check_warnings, parse_attempts
import time

path_to_log = '/var/log/auth.log'

def log_printer(log):
    with open(log) as file:


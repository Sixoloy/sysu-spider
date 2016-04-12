#! /usr/bin/env python
#coding=utf-8
import time, os, sched
from _bisect import __name__
schedule = sched.scheduler(time.time, time.sleep)
nTime = 1
def perform_command(cmd,inc):
    global nTime
    schedule.enter(inc, 0, perform_command(), (cmd,inc))
    print 'execute_time:' + str(time.time()), 'at nTime:' + str(nTime)
def timing_exe(cmd, inc = 60):
    schedule.enter(inc, 0, perform_command(), (cmd,inc))
    schedule.run()
if __name__ == '_main_':
    timing_exe("echo %time%", 5)
    
#!/usr/bin/env python

import sys
import htcondor
from htcondor import JobEventType
import os
from collections import defaultdict

from tabulate import tabulate
import curses

import time
import logging

logger = logging.getLogger( 'monitor' )
format = '%(levelname)s (%(name)s) [%(asctime)s]: %(message)s'
date = '%F %H:%M:%S'
logging.basicConfig( level='DEBUG', format=format, datefmt=date, filename='monitor_log.txt')

INTERVAL=5

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, curses.COLOR_WHITE, -1)

    directories = sys.argv[1:]

    def read_logs():
        log_list = []
        for directory in directories:
            for path, _, files in os.walk(directory):
                log_list.extend([os.path.join(path, x) for x in files if x.startswith("log_")])
        log_dict = {}
        for log in log_list:
            name = os.path.basename(log).replace("log_","").replace(".txt","")
            log_dict[name] = log
        return log_dict

    # Initiate new pad
    log_dict = read_logs()
    logger.info(f'Found {len(log_dict)} logs.')
    padlen = len(log_dict)+5
    pad = curses.newpad(padlen,curses.COLS)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    pad.nodelay(True)
    pad_pos = 0


    while True:
        pad.refresh( pad_pos, 0, 1, 1, curses.LINES-1, curses.COLS-1)

        colors = [3,3]
        try:
            table = []
            counter = 1
            for name, log in sorted(log_dict.items()):
                jel = htcondor.JobEventLog(log)
                first = None
                for event in jel.events(stop_after=0):
                    if not first:
                        first = event
                    latest = event
                try:
                    ret = latest["ReturnValue"]
                except KeyError:
                    ret = "-"
                if ret == 0:
                    colors.append(1)
                elif ret != "-":
                    colors.append(2)
                else:
                    colors.append(3)
                table.append([counter, name, latest.cluster, str(JobEventType.values[latest.type])])
                jel.close()
                counter += 1
            tab = tabulate(sorted(table), headers=["","Name", "Cluster", "Status", "Return"])
            for i,l in enumerate(tab.split('\n')):
                pad.addstr(i,0,l, curses.color_pair(colors[i]))


            # stdscr.refresh()
            # Scrolling
            start = time.time()
            stop = start
            while stop-start < INTERVAL:
                stop = time.time()

                pad.refresh( pad_pos, 0, 1, 1, curses.LINES-1, curses.COLS-1)
                cmd = stdscr.getch()
                if cmd == 'q':
                    sys.exit(0)
                elif  cmd == curses.KEY_HOME:
                    pad_pos = 0
                elif  cmd == curses.KEY_END:
                    pad_pos = len(log_dict) - curses.LINES + 1
                elif  cmd == curses.KEY_NPAGE:
                    pad_pos += 25
                elif  cmd == curses.KEY_PPAGE:
                    pad_pos -= 25
                elif  cmd == curses.KEY_DOWN:
                    pad_pos += 1
                elif cmd == curses.KEY_UP:
                    pad_pos -= 1

                # Post process
                if pad_pos < 0:
                    pad_pos = 0
                if pad_pos >= padlen:
                    pad_pos = padlen-1

                time.sleep(0.01)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    curses.wrapper(main)
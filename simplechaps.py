#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
simplechaps.py

Copyright 2012, Rogério Theodoro de Brito <rbrito@ime.usp.br>

Simple generator of chapter files suitable for use with mkvmerge when
creating a concatenated file from multiple video files (think: shows taken
from Youtube) and we want each of the multiple files to be have a
pointer/chapter marker for easy navigation.

We assume that the files to be concatenated are listed in the input file in
the format:

    name_1
    length_1
    name_2
    length_2
    ...
    name_n
    length_n

and that the order of the files is the intended, final order in which they
should appear in the concatenated file (this is the case when, say,
downloading a playlist with `youtube-dl` and using the autonumbering switch
`-A`).

The input in the format above can be generated by the use of `mediainfo` as
in:

    mediainfo --Inform='General;%Duration/String3%\n%FileName%\n' *.mp4 > input.txt
"""

import dateutil.parser
import re
import sys

from datetime import datetime


def time_to_timestamp(position):
    return float(dateutil.parser.parse('1970-01-01T%s UTC' %
                                       position).strftime('%s.%f'))

# Kludge, as I can't seem to get everyting normalized in UTC
EPOCH = time_to_timestamp('00:00:00')


def timestamp_to_hour(stamp):
    stamp = float(stamp)
    hh = int(stamp) / 3600
    mm = (int(stamp) % 3600) / 60
    ss = int(stamp) % 60
    uu = (stamp - int(stamp)) * 1000
    return '%02d:%02d:%02d.%03d' % (hh, mm, ss, uu)


def main():
    lines = sys.stdin.readlines()
    lines = [line.strip() for line in lines if line != '\n']

    # All times in the lines of the file are shifted by EPOCH and we unshift
    # them.
    cur_time = 0
    for i in range(0, len(lines), 2):
        normalized_name = lines[i+1].replace('_', ' ')
        normalized_name = re.sub('^\d+-','', normalized_name)
        print 'CHAPTER%02d=%s' % (i/2 + 1, timestamp_to_hour(cur_time))
        print 'CHAPTER%02dNAME=%s' % (i/2 + 1, normalized_name)
        cur_time += time_to_timestamp(lines[i]) - EPOCH


if __name__ == '__main__':
    main()

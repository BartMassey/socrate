#!/usr/bin/env python
# Copyright (c) 2011 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the end of this file for license terms.
# 
# Emit an infinite stream of weighted random
# student selections based on past history data.

# Bring in necessary modules
from argparse import *
from csv import *
from os import rename
from random import *

# Parse arguments
ap = ArgumentParser('Generate student Socratic callouts.')
ap.add_argument('callouts', type=int,
                help='how many callouts to generate')
ap.add_argument('--statefile', default='socrate.txt',
                help='Socrate state file')
ap.add_argument('--calloutfile', default='callout.txt',
                help='Socrate callout file')
args = ap.parse_args()

# Define class for individual students
class Socrate:
    index = None
    first = None
    last = None
    name = None
    count_called = None
    count_failed = None
    count_absent = None
    weight = None

    def __init__(self, fields):
        assert len(fields) == 6, 'bad list in initializer: ' + str(fields)
        [index_str, self.last, self.first,
         count_called_str, count_failed_str, count_absent_str] = fields
        self.name = self.first + ' ' + self.last
        self.index = int(index_str)
        self.count_called = int(count_called_str)
        self.count_failed = int(count_failed_str)
        self.count_absent = int(count_absent_str)
        self.calc_weight()

    def calc_weight(self):
        self.weight = \
          (1.0 + 0.5 * self.count_failed + 2 * self.count_absent) / \
          (self.count_called + 1) ** 2.0

    def call_on(self):
        self.count_called += 1
        self.calc_weight()

    def row(self):
        return [str(self.index), self.last, self.first,
                str(self.count_called),
                str(self.count_failed),
                str(self.count_absent)]

# Read in the statefile and calculate total weight
socrates = []
total_weight = 0.0
csv = reader(open(args.statefile, 'r'))
for line in csv:
    s = Socrate(line)
    socrates += [s]
    total_weight += s.weight

# Emit weighted random callouts to the callout file
with open(args.calloutfile, 'w') as cf:
    seed()
    for i in range(args.callouts):
        target_weight = uniform(0.0, total_weight)
        for s in socrates:
            target_weight -= s.weight
            if target_weight <= 0.0:
                break
        assert target_weight <= 0.0, "internal error: fell off end"
        total_weight -= s.weight
        s.call_on()
        total_weight += s.weight
        cf.print('%02d: %02d %s' % (i + 1, s.index, s.name))

# Write the new state file and clean up
newfile = args.statefile + '.new'
csv = writer(open(newfile, 'w'))
for s in socrates:
    csv.writerow(s.row())
rename(args.statefile, args.statefile + '.bak')
rename(newfile, args.statefile)

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall
# be included in all copies or substantial portions of the
# Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

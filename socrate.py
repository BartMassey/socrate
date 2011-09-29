# Copyright (c) 2011 Bart Massey
# 
# Emit an infinite stream of weighted random
# student selections based on past history data.

from argparse import *
from csv import *
from random import *

ap = ArgumentParser('Generate student Socratic callouts.')
ap.add_argument('callouts', type=int,
                help='how many callouts to generate')
ap.add_argument('--statefile', default='socrate.txt',
                help='Socrate state file')
args = ap.parse_args()

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

socrates = []
total_weight = 0.0
csv = reader(open(args.statefile, 'r'))
for line in csv:
    s = Socrate(line)
    socrates += [s]
    total_weight += s.weight

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
    print('%d: %d %s' % (i + 1, s.index, s.name))

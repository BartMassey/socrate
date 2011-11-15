#!/usr/bin/env python
# Copyright (c) 2011 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the end of this file for license terms.
# 
# GUI for random student selection based on past history
# data.

# Bring in necessary modules
from argparse import *
from csv import *
from os import rename
from random import *
from tkinter import *

# Parse arguments
ap = ArgumentParser("Generate student 'Socratic' callouts.")
ap.add_argument("--statefile", default="socrate.txt",
                help="Socrate state file")
args = ap.parse_args()

class Student:
    "Individual student data."
    index = None
    first = None
    last = None
    name = None
    count_called = None
    count_failed = None
    count_absent = None
    weight = None

    def __init__(self, fields):
        "Initialize a list of fields (from a CSV file)."
        assert len(fields) == 6, 'bad list in initializer: ' + str(fields)
        [index_str, self.last, self.first,
         count_called_str, count_failed_str, count_absent_str] = fields
        self.name = self.first + ' ' + self.last
        self.index = int(index_str)
        self.count_called = int(count_called_str)
        self.count_failed = int(count_failed_str)
        self.count_absent = int(count_absent_str)

    def weight(self):
        "Calculate a heuristic weight for the student. Returns a weight."
        return
          (1.0 + 0.5 * self.count_failed + 2 * self.count_absent) / \
          (self.count_called + 1) ** 2.0

    def call_on(self):
        "Mark the student as "called on" and recalc their weight"
        self.count_called += 1
        self.calc_weight()

    def row(self):
        "Return a string describing the student's current state"
        return [str(self.index), self.last, self.first,
                str(self.count_called),
                str(self.count_failed),
                str(self.count_absent)]

class Socrate(Frame):
    "GUI app for doing callouts"

    def __init__(self, statefile_name):
        "Read in the statefile."
        self.statefile_name = statefile_name
        self.socrates = []
        csv = reader(open(self.statefile_name, 'r'))
        for line in csv:
            s = Student(line)
            self.socrates += [s]

    def total_weight(self):
        "Calculate current total weight. Returns a weight."
        total_weight = 0
        for s in self.socrates:
            total_weight += s.weight()
        return total_weight
        

    def callout(self):
        "Call out a student. Returns a Student."
        target_weight = uniform(0.0, self.total_weight())
        for s in self.socrates:
            target_weight -= s.weight()
            if target_weight <= 0.0:
                break
        assert target_weight <= 0.0, "internal error: fell off end"
        self.log()


    def close(self):
        "Write the new state file and clean up."
        newfile = self.statefile_name + '.new'
        csv = writer(open(newfile, 'w'))
        for s in socrates:
            csv.writerow(s.row())
        rename(self.statefile_name, self.statefile_name + '.bak')
        rename(newfile, self.statefile_name)

# Seed the PRNG.
seed()

# Start the app.
app = Socrate(args.statefile)

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

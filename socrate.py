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
from time import ctime
from tkinter import *

# Width of student text display in chars
display_width = 35

# Parse arguments
ap = ArgumentParser("Generate student 'Socratic' callouts.")
ap.add_argument("--statefile", default="socrate.txt",
                help="Socrate state file")
ap.add_argument("--logfile", default="socrate-log.txt",
                help="Socrate log file")
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
        return \
          (1.0 + 0.5 * self.count_failed + 2 * self.count_absent) / \
          (self.count_called + 1) ** 2.0

    def call_on(self):
        "Mark the student as 'called on'"
        self.count_called += 1

    def mark_absent(self):
        "Mark the student as absent"
        self.count_absent += 1

    def mark_failed(self):
        "Mark the student as 'failed to answer'"
        self.count_failed += 1

    def row(self):
        "Return a list of strings describing the student's current state"
        return [str(self.index), self.last, self.first,
                str(self.count_called),
                str(self.count_failed),
                str(self.count_absent)]

    def fullname(self):
        return self.first + " " + self.last

    def index_str(self):
        return self.fullname() + " (" + str(self.index) + ")"

class Socrate(Frame):
    "GUI app for doing callouts"

    def __init__(self, root, statefile_name, logfile_name):
        """
        Read in the statefile and open the logfile. Set up
        the GUI.
        """
        global display_width
        # Read in the statefile.
        self.statefile_name = statefile_name
        self.students = []
        csv = reader(open(self.statefile_name, 'r'))
        for line in csv:
            s = Student(line)
            self.students += [s]
        # Set up the logfile.
        self.logfile_name = logfile_name
        self.logfile = open(self.logfile_name, 'a')
        self.log("started")
        # Set up the GUI.
        super(Socrate, self).__init__(root)
        self.grid()
        self.call = Button(self,
                           text = "Call",
                           command = self.do_callout)
        self.call.grid(row = 0, column = 0, sticky = E + W)
        self.ok = Button(self,
                         text = "OK",
                         command = self.do_ok)
        self.ok.grid(row = 1, column = 0, sticky = E + W)
        self.absent = Button(self,
                             text = "Absent",
                             command = self.do_absent)
        self.absent.grid(row = 2, column = 0, sticky = E + W)
        self.failed = Button(self,
                             text = "D/K",
                             command = self.do_failed)
        self.failed.grid(row = 3, column = 0, sticky = E + W)
        self.display = Label(self, width = display_width)
        self.display.grid(row = 0, column = 1)
        self.student = None
        self.update_gui()

    def configure_result_buttons(self, state):
        "Set the result buttons to the given state."
        self.ok.configure(state = state)
        self.absent.configure(state = state)
        self.failed.configure(state = state)

    def update_gui(self):
        if self.student == None:
            self.call.configure(state = NORMAL)
            self.configure_result_buttons(DISABLED)
        else:
            self.call.configure(state = DISABLED)
            self.configure_result_buttons(NORMAL)
        self.display_student()

    def do_callout(self):
        "Call out a student and display the result."
        if self.student != None:
            return
        self.student = self.callout()
        self.update_gui()

    def do_ok(self):
        "Prepare for the next student."
        self.student = None
        self.update_gui()

    def do_absent(self):
        "Mark the student absent. Log the mark."
        if self.student == None:
            return
        self.student.mark_absent()
        self.log("absent", self.student)
        self.student = None
        self.update_gui()

    def do_failed(self):
        "Mark the student failed. Log the mark."
        if self.student == None:
            return
        self.student.mark_failed()
        self.log("failed", self.student)
        self.student = None
        self.update_gui()

    def display_student(self):
        if self.student == None:
            text = ""
        else:
            text = self.student.index_str()
        self.display.configure(text = text, justify = LEFT)

    def log(self, message, student = None):
        "Log the given student and message, with a timestamp."
        self.logfile.write(ctime() + ": " + message)
        if student != None:
            self.logfile.write(" " + student.index_str())
        self.logfile.write("\n")
        self.logfile.flush()

    def total_weight(self):
        "Calculate current total weight. Returns a weight."
        total_weight = 0
        for s in self.students:
            total_weight += s.weight()
        return total_weight
        

    def callout(self):
        "Call out a student. Log the callout. Returns a Student."
        target_weight = uniform(0.0, self.total_weight())
        for s in self.students:
            target_weight -= s.weight()
            if target_weight <= 0.0:
                break
        assert target_weight <= 0.0, "internal error: fell off end"
        self.log("called", s)
        s.call_on()
        return s

    def close(self):
        "Write the new state file and clean up."
        newfile = self.statefile_name + '.new'
        csv = writer(open(newfile, 'w'))
        for s in self.students:
            csv.writerow(s.row())
        rename(self.statefile_name, self.statefile_name + '.bak')
        rename(newfile, self.statefile_name)
        self.log("finished")
        self.logfile.close()

# Seed the PRNG.
seed()

# Start the app.
root = Tk()
root.title("Socrate")
app = Socrate(root, args.statefile, args.logfile)
root.mainloop()
app.close()

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

'''
https://python-course.eu/tkinter/checkboxes-in-tkinter.php#:~:text=A%20Checkbox%20has%20two%20states,span%20more%20than%20one%20line.
'''

from tkinter import *


class Checkbar(Frame):
    def __init__(self, parent=None, picks=[], values=[], side=LEFT, anchor=W):
        Frame.__init__(self, parent)
        self.vars = []
        for pick in range(len(picks)):
            var = IntVar(value=values[pick])
            chk = Checkbutton(self, text=picks[pick], variable=var)
            chk.pack(side=side, anchor=anchor, expand=YES)
            self.vars.append(var)

    def state(self):
        return [x.get() for x in self.vars]

#!/usr/bin/python
from sigpyproc.Readers import *

import sys

FIL = sys.argv[1]
Tstart = float(sys.argv[2])
Tend = float(sys.argv[3])
Tblock = Tend - Tstart

F = FilReader(FIL)
Tsamp = F.header['tsamp']

Start = int(Tstart/Tsamp)
End = int(Tblock/Tsamp)

F.split(Start,End)

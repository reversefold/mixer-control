#!/usr/bin/env python3
import sys
from typing import List, Tuple

import serial


import serial.tools.list_ports as port_list

ports = list(port_list.comports())
for p in ports:
    print(p)


## Config
PORT = "COM8"
BAUD = 9600
# Weight of new values in exponential moving averages (EMA)
WEIGHT = 0.2
# Amount of change that constitutes a definite change (higher for lower quality components, lower for higher quality components)
DELTA = 15


## Global constants
MINVAL = 0
MAXVAL = 1023
INV_WEIGHT = 1.0 - WEIGHT


with serial.Serial(PORT, BAUD, timeout=1) as ser:
    print(ser.name)

    vals: List[Tuple[float, float, float, float]] = []

    while True:
        line = ser.readline().decode("utf8", errors="replace").strip()
        values = [int(s) for s in line.split("|")]
        if not vals:
            vals = [(float(v), float(v), 0, float(v)) for v in values]
        else:
            for i, ((_, aval, dval, oval), rawval) in enumerate(zip(vals, values)):
                # EMA of the signal to reduce noise
                nval = INV_WEIGHT * aval + WEIGHT * rawval
                # EMA of the distance between the output value and the raw value to decide if we're getting noise or a real change
                dval = INV_WEIGHT * dval + WEIGHT * (rawval - oval)
                if MAXVAL - nval < DELTA:
                    oval = MAXVAL
                    dval = 0
                elif nval - MINVAL < DELTA:
                    oval = MINVAL
                    dval = 0
                elif abs(dval) > DELTA:
                    oval = nval
                    dval = 0
                vals[i] = (rawval, nval, dval, oval)
        print(" | ".join(" ".join(f"{val:7.2f}" for val in tup) for tup in vals))

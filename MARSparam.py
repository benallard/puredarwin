"""
MARS Parameters
"""

from myhdl import intbv

CORESIZE = 8000

AddrWidth = len(intbv(min=0, max=CORESIZE))

MAXPROCESSES = CORESIZE/16

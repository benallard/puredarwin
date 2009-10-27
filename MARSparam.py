"""
MARS Parameters
"""

from myhdl import intbv, enum

CORESIZE = 8000

AddrWidth = len(intbv(min=0, max=CORESIZE))

MAXPROCESSES = CORESIZE/16

# Constant for the Size of an Instruction
# usefull for slicing
InstrWidth = 14 + 2 * AddrWidth

ReadRange = 400
WriteRange = 400

t_Modifier = enum("IMMEDIATE", "DIRECT",
                   "A_INDIRECT", "A_DECREMENT", "A_INCREMENT",
                   "B_INDIRECT", "B_DECREMENT", "B_INCREMENT")

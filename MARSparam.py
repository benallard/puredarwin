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

class we:
    OpCode = intbv("100000")
    Modif  = intbv("010000")
    AMod   = intbv("001000")
    ANum   = intbv("000100")
    BMod   = intbv("000010")
    BNum   = intbv("000001")

class t_OpCode:
    DAT, MOV, ADD, SUB, MUL, DIV, MOD, JMP, JMZ, JMN, DJN, CMP, SNE, SLT, SPL, NOP = range(16)
    SEQ = CMP

class t_Modifier:
    A, B, AB, BA, F, X, I = range(7)

class t_Mode:
    IMMEDIATE, DIRECT, A_INDIRECT, A_DECREMENT, A_INCREMENT, B_INDIRECT, B_DECREMENT, B_INCREMENT = range(8)

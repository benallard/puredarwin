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
    Full   = OpCode | Modif | AMod | ANum | BMod | BNum
    A      = ANum
    B      = BNum
    AB     = BNum
    BA     = ANum
    F      = ANum | BNum
    X      = ANum | BNum
    I      = Full

class t_OpCode:
    DAT, MOV, ADD, SUB, MUL, DIV, MOD, JMP, JMZ, JMN, DJN, CMP, SNE, SLT, SPL, NOP = [intbv(i)[5:] for i in range(16)]
    SEQ = CMP

class t_Modifier:
    A, B, AB, BA, F, X, I = [intbv(i)[3:] for i in range(7)]

class t_Mode:
    IMMEDIATE, DIRECT, A_INDIRECT, A_DECREMENT, A_INCREMENT, B_INDIRECT, B_DECREMENT, B_INCREMENT = [intbv(i)[3:] for i in range(8)]


    @classmethod
    def __getitem__(key):

        if (type(key) != "str")  or (len(key) != 1):
            raise TypeError("Wrong type")

        if key == '#':
            return IMMEDIATE
        elif key == '$':
            return DIRECT
        elif key == '*':
            return A_INIDRECT
        elif key == '@':
            return B_INDIRECT
        elif key == '{':
            return A_DECREMENT
        elif key == '<':
            return B_DECREMENT
        elif key == '}':
            return A_INCREMENT
        elif key == '>':
            return B_INCREMENT
        else:
            raise KeyError("Modifier %s not defined" % name)


class Addr(intbv):

    def __init__(self, val=0):
        intbv.__init__(self, val, min=0, max=CORESIZE)

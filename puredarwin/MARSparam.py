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
        if val < 0:
            val = (val + CORESIZE) % CORESIZE
        intbv.__init__(self, val, min=0, max=CORESIZE)

class Instr(intbv):
    def __init__(self, OpCode=None, Modifier=None, AMode=None, ANumber=None, BMode=None, BNumber=None, val=None):
        if not val:
            val = 0
        intbv.__init__(self, val, _nrbits=InstrWidth)
        if OpCode:
            self[InstrWidth:InstrWidth-5] = OpCode
        if Modifier:
            self[InstrWidth-5:InstrWidth-8] = Modifier
        if AMode:
            self[InstrWidth-8:InstrWidth-11] = AMode
        if ANumber:
            self[InstrWidth-11:InstrWidth-11-AddrWidth] = ANumber
        if BMode:
            self[AddrWidth+3:AddrWidth] = BMode
        if BNumber:
            self[AddrWidth:] = BNumber

    def __getattr__(self, name):
        if name == "OpCode":
            return self[InstrWidth:InstrWidth-5]
        elif name == "Modifier":
            return self[InstrWidth-5:InstrWidth-8]
        elif name == "AMode":
            return self[InstrWidth-8:InstrWidth-11]
        elif name == "ANumber":
            return self[InstrWidth-11:InstrWidth-11-AddrWidth]
        elif name == "BMode":
            return self[AddrWidth+3:AddrWidth]
        elif name == "BNumber":
            return self[AddrWidth:0]
        else:
            return intbv.__getattr__(name)

    def __setattr__(self, name, value):
        if name == "OpCode":
            self[InstrWidth:InstrWidth-5] = value
        elif name == "Modifier":
            self[InstrWidth-5:InstrWidth-8] = value
        elif name == "AMode":
            self[InstrWidth-8:InstrWidth-11] = value
        elif name == "ANumber":
            self[InstrWidth-11:InstrWidth-11-AddrWidth] = value
        elif name == "BMode":
            self[AddrWidth+3:AddrWidth] = value
        elif name == "BNumber":
            self[AddrWidth:0] = value
        else:
            intbv.__setattr__(self, name,value)

    def __str__(self):
        return "%s_%s_%s_%s_%s_%s" % (self.OpCode, self.Modifier, self.AMode, self.ANumber, self.BMode, self.BNumber)

    def __copy__(self):
        return Instr(val=self)

    def __deepcopy__(self, visit):
        return Instr(val=self)

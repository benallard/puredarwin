"""
This is the processor of the MARS

We will try to keep it as quick as possible ...
"""

from myhdl import *

import MARSparam
from MARSparam import t_OpCode, t_Modifier, t_Mode
from MARSparam import InstrWidth

def EvalOp(Mod, Number, Ptr, WData, we, RData, clk):
    """
    Eval A operand (Or actually B operand)

    assumption:
    Rdata = Core[Number + IP]
    WAddr == Number


    We don'y take any reset as input as we don't keep any internal state ...

    """

    @always(clk.posedge)
    def fsm():
        we.next = 0

        if Mod == t_Mode.IMMEDIATE:
            Ptr.next = 0
        elif Mod == t_Mode.DIRECT:
            Ptr.next = Number

        elif Mod == t_Mode.A_INDIRECT:
            Ptr.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + Number
        elif Mod == t_Mode.A_INCREMENT:
            Ptr.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + Number + 1
            we.next = MARSparam.we.ANum
            WData.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + 1
        elif Mod == t_Mode.A_DECREMENT:
            Ptr.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + Number - 1
            we.next = MARSparam.we.ANum
            WData.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] - 1

        elif Mod == t_Mode.B_INDIRECT:
            Ptr.next = RData[MARSparam.AddrWidth:0] + Number
        elif Mod == t_Mode.B_INCREMENT:
            Ptr.next = RData[MARSparam.AddrWidth:0] + Number + 1
            we.next = MARSparam.we.BNum
            WData.next = RData[MARSparam.AddrWidth:0] + 1
        elif Mod == t_Mode.B_DECREMENT:
            Ptr.next = RData[MARSparam.AddrWidth:0] + Number - 1
            we.next = MARSparam.we.BNum
            WData.next = RData[MARSparam.AddrWidth:0] - 1
        else:
            raise ValueError("Mod: %d not understood" % Mod)

    return fsm

def OutQueue(OpCode, RPA, PC, IPout1, we1, IPout2, we2, clk):
    """
    The Exec part that output to the TaskQueue

    """

    @always(clk.posedge)
    def Out1():
        we1.next = OpCode != t_OpCode.DAT
        if OpCode in (t_OpCode.MOV,
                      t_OpCode.ADD,
                      t_OpCode.SUB,
                      t_OpCode.MUL,
                      t_OpCode.SPL,
                      t_OpCode.NOP):
            IPout1.next = (PC + 1) % MARSparam.CORESIZE
        elif OpCode is t_OpCode.JMP:
            IPOut1.next = RPA
        else:
            raise NotImplementedError("Only few OpCode are Implemented")

    @always(clk.posedge)
    def Out2():
        we2.next = False
        if OpCode is t_OpCode.SPL:
            IPOut2.next = RPA
            we2.next = True

    return Out1, Out2

def OutCore(OpCode, Modif, IRA, IRB, we, WData, DivByZero, clk):
    """
    WPA is not used anymore at this stage
    RPA is only used to Queue

    RPB is not used any more at this stage
    WPB is used for every write

    assumption:
    WAddr == BPtr

    Any division by Zero is killing the current task
    """

    @always(clk.posedge)
    def comb():
        we.next = 0
        if OpCode in (t_OpCode.DAT,
                      t_OpCode.JMP,
                      t_OpCode.JMZ,
                      t_OpCode.JMN,
                      t_OpCode.CMP,
                      t_OpCode.SNE,
                      t_OpCode.SLT,
                      t_OpCode.SPL,
                      t_OpCode.NOP):
            # Those don't touch the Core
            pass

        elif OpCode == t_OpCode.MOV:
            if Modif == t_Modifier.A:
                WData.next = IRA
                we.next = MARSparam.we.ANum
            elif Modif == t_Modifier.B:
                WData.next = IRA
                we.next = MARSparam.we.BNum
            elif Modif == t_Modifier.AB:
                WData.next = concat(intbv(0)[MARSparam.AddrWidth:], # pading
                                    IRA[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth]) # ANum
                we.next = MARSparam.we.BNum
            elif Modif == t_Modifier.BA:
                WData.next = concat(intbv(0)[InstrWidth-11:], # pading
                                    IRA[MARSparam.AddrWidth:0], # BNum
                                    intbv(0)[MARSparam.AddrWidth+3:]) # pading
                we.next = MARSparam.we.ANum
            elif Modif == t_Modifier.F:
                WData.next = IRA
                we.next = MARSparam.we.ANum | MARSparam.we.BNum
            elif Modif == t_Modifier.X:
                WData.next = concat(intbv(0)[InstrWidth-11:], # pading
                                    IRA[MARSparam.AddrWidth:0], # BNum
                                    intbv(0)[3:], # pading
                                    IRA[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth]) # ANum
                we.next = MARSparam.we.ANum | MARSparam.we.BNum
            elif Modif == t_Modifier.I:
                WData.next = IRA
                we.next = intbv("111111")
            else:
                raise ValueError("Modifier %d not supported" % Modif)

        else:
            raise NotImplementedError("Only few OpCode are implemented")

    return comb

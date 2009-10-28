"""
This is the processor of the MARS

We will try to keep it as quick as possible ...
"""

from myhdl import *

import MARSparam
from MARSparam import t_Mode
from MARSparam import InstrWidth

# Addr and Addr == Number
def EvalOp(Mod, Number, Ptr, WData, we, RData, clk):
    """
    Eval A operand (Or actually B operand)

    assumption:
    Rdata = Core[XNumber + IP]


    We don'y take any reset as input as we don't keep any internal state ...

    """

    we_ANum_only = intbv("000100")
    we_BNum_only = intbv("000001")

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
            we.next = we_ANum_only
            WData.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + 1
        elif Mod == t_Mode.A_DECREMENT:
            Ptr.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + Number - 1
            we.next = we_ANum_only
            WData.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] - 1

        elif Mod == t_Mode.B_INDIRECT:
            Ptr.next = RData[MARSparam.AddrWidth:0] + Number
        elif Mod == t_Mode.B_INCREMENT:
            Ptr.next = RData[MARSparam.AddrWidth:0] + Number + 1
            we.next = we_BNum_only
            WData.next = RData[MARSparam.AddrWidth:0] + 1
        elif Mod == t_Mode.B_DECREMENT:
            Ptr.next = RData[MARSparam.AddrWidth:0] + Number - 1
            we.next = we_BNum_only
            WData.next = RData[MARSparam.AddrWidth:0] - 1
        else:
            raise ValueError("Mod: %d not understood" % Mod)

    return fsm


"""
This is the processor of the MARS

We will try to keep it as quick as possible ...
"""

from myhdl import *

import MARSparam
from MARSparam import t_Modifier
from MARSparam import InstrWidth

# Addr and Addr == Number
def EvalOp(Modif, Number, Ptr, Wdata, we, Rdata, clk):
    """
    Eval A operand (Or actually B operand)

    assumption:
    Rdata = Core[XNumber + IP]


    We don'y take any reset as input as we don't keep any internal state ...

    """

    we_ANum_only = intbv("000100")
    we_BNum_only = intbv("000101")

    @always(clk.posedge)
    def fsm():
        we.next = 0

        if Modif == t_Modifier.IMMEDIATE:
            Ptr.next = 0
        elif Modif == t_Modifier.DIRECT:
            Ptr.next = Number

        elif Modif == t_Modifier.A_INDIRECT:
            Ptr.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth]
        elif Modif == t_Modifier.A_INCREMENT:
            Ptr.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + Number + 1
            we.next = we_ANum_only
            WData.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + 1
        elif Modif == t_Modifier.A_DECREMENT:
            Ptr.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + Number - 1
            we.next = we_ANum_only
            WData.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] - 1

        elif Modif == t_Modifier.B_INDIRECT:
            Ptr.next = RData[MARSparam.AddrWidth:0]
        elif Modif == t_Modifier.B_INCREMENT:
            Ptr.next = RData[MARSparam.AddrWidth:0] + Number + 1
            we.next = we_BNum_only
            WData.next = RData[MARSparam.AddrWidth:0] + 1
        elif Modif == t_Modifier.B_DECREMENT:
            Ptr.next = RData[MARSparam.AddrWidth:0] + Number - 1
            we.next = we_BNum_only
            WData.next = RData[MARSparam.AddrWidth:0] - 1

    return fsm

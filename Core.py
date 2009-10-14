"""
This is the Core of the MARS.

This is the central memory storage for the Warriors, the "Hill"
"""

from myhdl import *

import MARSparam
from MARSparam import InstrWidth

def RAM(dout, din, addr, we, clk, rst_n, width, depth):
    """ Basic RAM model """
    
    mem = [Signal(intbv(0)[width:]) for i in range(depth)]

    @always(clk.posedge)
    def write():
        if we:
            mem[int(addr)].next = din

    @always_comb
    def read():
        dout.next = mem[int(addr)]

    return read, write

def Core(addr, din, dout, we, clk, rst_n, maxSize):
    """ Our Core """


    opcode_out = Signal(intbv(0)[5:])
    modif_out = Signal(intbv(0)[3:])
    amode_out = Signal(intbv(0)[3:])
    anumber_out = Signal(intbv(0)[MARSparam.AddrWidth:])
    bmode_out = Signal(intbv(0)[3:])
    bnumber_out = Signal(intbv(0)[MARSparam.AddrWidth:])

    opcode_in = Signal(intbv(0)[5:])
    modif_in = Signal(intbv(0)[3:])
    amode_in = Signal(intbv(0)[3:])
    anumber_in = Signal(intbv(0)[MARSparam.AddrWidth:])
    bmode_in = Signal(intbv(0)[3:])
    bnumber_in = Signal(intbv(0)[MARSparam.AddrWidth:])

    # Those are VHDL Aliases
    @always_comb
    def comb():
        opcode_in.next = din[InstrWidth:InstrWidth-5]
        dout.next[InstrWidth:InstrWidth-5] = opcode_out

        modif_in.next = din[InstrWidth-5:InstrWidth-8]
        dout.next[InstrWidth-5:InstrWidth-8] = modif_out

        amode_in.next = din[InstrWidth-8:InstrWidth-11]
        dout.next[InstrWidth-8:InstrWidth-11] = amode_out

        anumber_in.next = din[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth]
        dout.next[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] = anumber_out

        bmode_in.next = din[MARSparam.AddrWidth+3:MARSparam.AddrWidth]
        dout.next[MARSparam.AddrWidth+3:MARSparam.AddrWidth] = bmode_out

        bnumber_in.next = din[MARSparam.AddrWidth:0]
        dout.next[MARSparam.AddrWidth:0] = bnumber_out

    # My RAMs
    OpCode = RAM(opcode_out, opcode_in, addr, we[5] , clk, rst_n, 5, maxSize)
    Modif = RAM(modif_out, modif_in, addr, we[4], clk, rst_n, 3, maxSize)
    AMode = RAM(amode_out, amode_in, addr, we[3], clk, rst_n, 3, maxSize)
    ANumber = RAM(anumber_out, anumber_in, addr, we[2], clk, rst_n, MARSparam.AddrWidth, maxSize)
    BMode = RAM(bmode_out, bmode_in, addr, we[1], clk, rst_n, 3, maxSize)
    BNumber = RAM(bnumber_out, bnumber_in, addr, we[0], clk, rst_n, MARSparam.AddrWidth, maxSize)

    return OpCode, Modif, AMode, ANumber, BMode, BNumber, comb

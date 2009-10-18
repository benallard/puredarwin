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

def Fold(AddressIn, AddressOut, limit, maxSize):

    Address_i = Signal(intbv(min = 0, max = MARSparam.CORESIZE))

    @always_comb
    def comb():
        if (AddressIn % limit) > (limit/2):
            AddressOut.next = (AddressIn % limit) + maxSize - limit
        else:
            AddressOut.next = AddressIn % limit

    return comb

def Core(pc, waddr, din, raddr, dout, we, clk, rst_n, maxSize):
    """ Our Core """

    opcode_we, modif_we, amode_we, anumber_we, bmode_we, bnumber_we = [Signal(bool()) for i in range (6)]

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

        opcode_we.next = we[5]
        modif_we.next = we[4]
        amode_we.next = we[3]
        anumber_we.next = we[2]
        bmode_we.next = we[1]
        bnumber_we.next = we[0]

    # My RAMs
    OpCode = RAM(opcode_out, opcode_in, addr, opcode_we , clk, rst_n, 5, maxSize)
    Modif = RAM(modif_out, modif_in, addr, modif_we, clk, rst_n, 3, maxSize)
    AMode = RAM(amode_out, amode_in, addr, amode_we, clk, rst_n, 3, maxSize)
    ANumber = RAM(anumber_out, anumber_in, addr, anumber_we, clk, rst_n, MARSparam.AddrWidth, maxSize)
    BMode = RAM(bmode_out, bmode_in, addr, bmode_we, clk, rst_n, 3, maxSize)
    BNumber = RAM(bnumber_out, bnumber_in, addr, bnumber_we, clk, rst_n, MARSparam.AddrWidth, maxSize)

    return OpCode, Modif, AMode, ANumber, BMode, BNumber, comb

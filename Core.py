"""
This is the Core of the MARS.

This is the central memory storage for the Warriors, the "Hill"
"""

from myhdl import *

import MARSparam
from MARSparam import InstrWidth

def RAM(raddr, dout, waddr, din, we, clk, rst_n, width, depth):
    """ Basic RAM model """
    
    mem = [Signal(intbv(0)[width:]) for i in range(depth)]

    @always(clk.posedge)
    def write():
        if we:
            mem[int(waddr)].next = din

    @always_comb
    def read():
        dout.next = mem[int(raddr)]

    return read, write

def Fold(PC, AddressIn, AddressOut, limit, maxSize):

    AddrIn_fold, AddrIn_limit = [Signal(intbv(0, min=0, max=MARSparam.CORESIZE)) for i in range(2)]

    @always_comb
    def comb1():
        AddrIn_limit.next = AddressIn % limit

    @always_comb
    def comb2():
        if (AddrIn_limit) > (limit/2):
            AddrIn_fold.next = (AddrIn_limit) + maxSize - limit
        else:
            AddrIn_fold.next = AddrIn_limit

    @always_comb
    def comb3():
        AddressOut.next = (PC + AddrIn_fold) % maxSize

    return comb1, comb2, comb3

def Core(pc, waddr, din, raddr, dout, we, clk, rst_n, maxSize):
    """ Our Core """

    raddr_i, waddr_i = [Signal(intbv(0, min=0, max=MARSparam.CORESIZE)) for i in range(2)]

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
    def split():
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

    @always(raddr_i, waddr_i)
    def verbose():
        print "R: PC: %d, Ofs: %d ==> %d" % (pc, raddr, raddr_i)
        print "W: PC: %d, Ofs: %d ==> %d" % (pc, waddr, waddr_i)

    ReadFold = Fold(pc, raddr, raddr_i, MARSparam.ReadRange, MARSparam.CORESIZE)
    WriteFold = Fold(pc, waddr, waddr_i, MARSparam.WriteRange, MARSparam.CORESIZE)


    # My RAMs
    OpCode = RAM(raddr_i, opcode_out, waddr_i, opcode_in, opcode_we , clk, rst_n, 5, maxSize)
    Modif = RAM(raddr_i, modif_out, waddr_i, modif_in, modif_we, clk, rst_n, 3, maxSize)
    AMode = RAM(raddr_i, amode_out, waddr_i, amode_in, amode_we, clk, rst_n, 3, maxSize)
    ANumber = RAM(raddr_i, anumber_out, waddr_i, anumber_in, anumber_we, clk, rst_n, MARSparam.AddrWidth, maxSize)
    BMode = RAM(raddr_i, bmode_out, waddr_i, bmode_in, bmode_we, clk, rst_n, 3, maxSize)
    BNumber = RAM(raddr_i, bnumber_out, waddr_i, bnumber_in, bnumber_we, clk, rst_n, MARSparam.AddrWidth, maxSize)

    return OpCode, Modif, AMode, ANumber, BMode, BNumber, ReadFold, WriteFold, split, verbose

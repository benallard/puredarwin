"""
This is the Core of the MARS.

This is the central memory storage for the Warriors, the "Hill"
"""

from myhdl import *

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

def Core(addr, clk, rst_n, maxSize):
    """ Our Core """

    OpCode = RAM(opcode_out, opcode_in, opcode_addr, opcode_we, clk, 5, maxSize)
    Modif = RAM(modif_out, modif_in, modif_addr, modif_we, clk, 3, maxSize)
    AMode = RAM(amode_out, amode_in, amode_addr, amode_we, clk, 3, maxSize)
    ANumber = RAM(number_out, anumber_in, anumber_addr, anumber_we, clk, MARSparam.AddrWidth, maxSize)
    BMode = RAM(bmode_out, bmode_in, bmode_addr, bmode_we, clk, 3, maxSize)
    BNumber = RAM(bnumber_out, bnumber_in, bnumber_addr, bnumber_we, clk, MARSparam.AddrWidth, maxSize)
    
    return OpCode, Modif, AMode, ANumber, BMode, BNumber

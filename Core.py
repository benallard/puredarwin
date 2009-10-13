"""
This is the Core of the MARS.

This is the central memory storage for the Warriors, the "Hill"
"""

from myhdl import *

import MARSparam

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

    # Constant for the Size of an Instruction
    # usefull for slicing
    InstrWidth = 14 + 2 * MARSparam.AddrWidth

    # Those are VHDL Aliases
    opcode_in = din[InstrWidth:InstrWidth-5]
    dout[InstrWidth:InstrWidth-5] = opcode_out

    modif_in = din[InstrWidth-5:InstrWidth-8]
    dout[InstrWidth-5:InstrWidth-8] = modif_out

    amode_in = din[InstrWidth-8:InstrWidth-11]
    dout[InstrWidth-8:InstrWidth-11] = amode_out

    anumber_in = din[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth]
    dout[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] = anumber_out

    bmode_in = din[MARSparam.AddrWidth+3:MARSparam.AddrWidth]
    dout[MARSparam.AddrWidth+3:MARSparam.AddrWidth] = bmode_out

    bnumber_in = din[MARSparam.AddrWidth:0]
    dout[MARSparam.AddrWidth:0] = bnumber_out

    opcode_we = we[6:5]
    modif_we = we[5:4]
    amode_we = we[4:3]
    anumber_we = we[3:2]
    bmode_we = we[2:1]
    bnumber_we = we[1:0]

    # My RAMs
    OpCode = RAM(opcode_out, opcode_in, addr, opcode_we, clk, rst_n, 5, maxSize)
    Modif = RAM(modif_out, modif_in, addr, modif_we, clk, rst_n, 3, maxSize)
    AMode = RAM(amode_out, amode_in, addr, amode_we, clk, rst_n, 3, maxSize)
    ANumber = RAM(number_out, anumber_in, addr, anumber_we, clk, rst_n, MARSparam.AddrWidth, maxSize)
    BMode = RAM(bmode_out, bmode_in, addr, bmode_we, clk, rst_n, 3, maxSize)
    BNumber = RAM(bnumber_out, bnumber_in, addr, bnumber_we, clk, rst_n, MARSparam.AddrWidth, maxSize)

    @always_comb
    def comb():
        pass

    return OpCode, Modif, AMode, ANumber, BMode, BNumber, comb

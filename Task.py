"""
This is the Task Queue of the MARS
"""

from myhdl import *

import MARSparam

def FIFO(dout, din, re, we, empty, clk, rst_n, maxFilling, ID = None):
    """ Fifo that fits our need: without full flag """

    content = []

    @always(clk.posedge, rst_n.negedge)
    def access():
        if rst_n == False:
            del content[:] # that one is tricky ...
        elif clk == True:
            if ID != None:
                print "FIFO::%d (%d) we:%s re:%s " % (ID, len(content), we, re)
            if we:
                if (len(content) < maxFilling):
                    content.insert(0, din.val)
            if re:
                dout.next = content.pop()
        empty.next = (len(content) == 0)

    return access

def TaskQueue(Warrior, IPin, IPout, re, we, empty, clk, rst_n, maxWarriors):
    
    dout_i = [Signal(intbv(0)[MARSparam.AddrWidth:]) for i in range(maxWarriors)]
    din_i = [Signal(intbv(0)[MARSparam.AddrWidth:]) for i in range(maxWarriors)]
    re_i = [Signal(bool(False)) for i in range(maxWarriors)]
    we_i = [Signal(bool(False)) for i in range(maxWarriors)]
    empty_i = [Signal(bool(True)) for i in range(maxWarriors)]
    clk_i = [Signal(bool(False)) for i in range(maxWarriors)]
    queue = [FIFO(dout_i[i], din_i[i], re_i[i], we_i[i], empty_i[i], clk_i[i], rst_n, MARSparam.MAXPROCESSES, ID=i) for i in range(maxWarriors)]

    @always_comb
    def comb():
        """ Combinationnal part
            That basically is a big MUX

        in:
          - dout_i
          - IPin
          - re
          - we
          - empty_i
          - Warrior
        out:
          - IPout
          - din_i
          - re_i
          - we_i
          - empty
        """
        IPout.next = dout_i[int(Warrior)]
        din_i[int(Warrior)].next = IPin
        re_i[int(Warrior)].next = re
        we_i[int(Warrior)].next = we
        empty.next = empty_i[int(Warrior)]
        clk_i[int(Warrior)].next = clk

    @always(clk)
    def shooter():
        clk_i[int(Warrior)].next = clk 

    return queue, comb

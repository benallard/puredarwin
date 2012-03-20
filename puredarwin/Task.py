"""
This is the Task Queue of the MARS
"""

from myhdl import *

import MARSparam

def FIFO(dout, din1, we1, din2, we2, re, empty, clk, rst_n, maxFilling, ID = None):
    """ Fifo that fits our need: without full flag """

    content = []

    @always(clk.posedge, rst_n.negedge)
    def access():
        if rst_n == False:
            del content[:] # that one is tricky ...
        elif clk == True:
            if ID != None:
                print "FIFO::%d (%d) we1:%s we2:%s re:%s " % (ID, len(content), we1, we2, re)
            if we1:
                if (len(content) < maxFilling):
                    content.insert(0, din1.val)
            if we2:
                if not we1:
                    raise ValueError("Writing to second channel when First one not used")
                if (len(content) < maxFilling):
                    content.insert(0, din2.val)

            if re:
                dout.next = content.pop()
        empty.next = (len(content) == 0)

    return access

def TaskQueue(Warrior, IPin1, IPin2, IPout, re, we1, we2, empty, clk, rst_n, maxWarriors, maxFilling=MARSparam.MAXPROCESSES):
    
    dout_i = [Signal(intbv(0)[MARSparam.AddrWidth:]) for i in range(maxWarriors)]
    din1_i, din2_i = [[Signal(intbv(0)[MARSparam.AddrWidth:]) for i in range(maxWarriors)]for i in range(2)]
    re_i = [Signal(bool(False)) for i in range(maxWarriors)]
    we1_i, we2_i = [[Signal(bool(False)) for i in range(maxWarriors)] for i in range (2)]
    empty_i = [Signal(bool(True)) for i in range(maxWarriors)]
    clk_i = [Signal(bool(False)) for i in range(maxWarriors)]
    queue = [FIFO(dout=dout_i[i],
                  din1=din1_i[i],
                  din2=din2_i[i],
                  re=re_i[i],
                  we1=we1_i[i],
                  we2=we2_i[i],
                  empty=empty_i[i],
                  clk=clk_i[i],
                  rst_n=rst_n,
                  maxFilling=maxFilling,
                  ID=i)
             for i in range(maxWarriors)]

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
        din1_i[int(Warrior)].next = IPin1
        din2_i[int(Warrior)].next = IPin2
        re_i[int(Warrior)].next = re
        we1_i[int(Warrior)].next = we1
        we2_i[int(Warrior)].next = we2
        empty.next = empty_i[int(Warrior)]
        clk_i[int(Warrior)].next = clk

    @always(clk)
    def shooter():
        clk_i[int(Warrior)].next = clk 

    return queue, comb

"""
This is the Task Queue of the MARS
"""

from myhdl import *

from . import MARSparam


def FIFO(dout, din1, we1, din2, we2, re, empty, clk, rst_n, maxFilling, ID = None):
    """ Fifo that fits our need: without external full flag
    """

    content = [Signal(intbv(0)[MARSparam.AddrWidth:]) for i in range(maxFilling)]
    bottom = Signal(modbv(maxFilling, min=0, max=maxFilling))
    currentFilling = Signal(intbv(0, min=0, max=maxFilling+1))

    @always(clk.posedge)
    def display():
        if ID is not None:
            print("FIFO::%d (%d/%d) we1:%s we2:%s re:%s " % (ID, currentFilling, maxFilling, we1, we2, re))
            if len(content) < 10: print(content, bottom)

    @always_seq(clk.posedge, reset=rst_n)
    def write():
        free = maxFilling - currentFilling + int(re)
        if we1 and we2:
            # Need to add 2 elements
            if free >= 1:
                content[modbv(bottom + currentFilling, min=0, max=maxFilling)].next = din1
            if free >= 2:
                content[modbv(bottom + currentFilling + 1, min=0, max=maxFilling)].next = din2
        elif we1:
            # Need to add only one element
            if free >= 1:
                content[modbv(bottom + currentFilling, min=0, max=maxFilling)].next = din1
        elif we2 and not we1:
            raise ValueError("Writing to second channel when First one not used")

    @always_seq(clk.posedge, reset=rst_n)
    def filling():
        free = maxFilling - currentFilling
        needed = int(we1) + int(we2)

        if free < needed:
            currentFilling.next = currentFilling + free - int(re)
        else:
            currentFilling.next = currentFilling + needed - int(re)

    @always_seq(clk.posedge, reset=rst_n)
    def read():
        if re: # and (currentFilling > 0):  # Shouldn't be necessary as we don't empty empty FIFOS
            dout.next = content[bottom]
            bottom.next = bottom + 1

    @always_comb
    def comb():
        empty.next = currentFilling == 0

    return display, write, read, comb, filling

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

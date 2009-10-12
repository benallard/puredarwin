"""
This is the Task Queue of the MARS
"""

from myhdl import *

def FIFO(dout, din, re, we, empty, clk, maxFilling):
    """ Fifo that fits our need: without full flag """

    content = []

    @always(clk.posedge)
    def access():
        if we:
            if (len(content) < maxFilling):
                content.insert(0, din.val)
        if re:
            dout.next = content.pop()
        empty.next = (len(content) == 0)

    return access

def TaskQueue(Warrior, clk, Warriors, MAXPROCESSES):
    
    queue = [FIFO(dout, din, re, we, empty, clk) for i in range(Warriors)]

    return queue

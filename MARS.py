
from myhdl import *

import MARSparam
from MARSparam import *

from Proc import Proc
from Core import Core
from Task import TaskQueue
from Loader import Loader

InstrEmpty = Instr(t_OpCode.DAT, t_Modifier.F, t_Mode.DIRECT, Addr(), t_Mode.DIRECT, Addr())

def MARS(clk, rst_n, req, ack, RX_load, draw, Winner, nbWarriors, maxTime):
    """ MARS is the reunion of the modules """  

    t_State=enum("IDLE", "LOAD", "FETCH", "PROC")

    state = Signal(t_State.IDLE)
    prevWarrior, Warrior = [Signal(intbv(0, min=0, max=nbWarriors)) for i in range(2)]
    Time = Signal(intbv(0, min=0, max=maxTime))

    IP1_i, IP1_proc, IP1_load, PC_i, IP2_i, WOfs_i, ROfs = [Signal(Addr(0)) for i in range (7)]
    we1_i, we1_load, we1_proc, we2_i, req_proc, ack_proc, req_load, ack_load, re_i, empty_i = [Signal(bool()) for i in range(10)]
    Instr_i = Signal(Instr())
    WData_i, RData_i, Dout_load, Dout_proc = [Signal(intbv(0)[MARSparam.InstrWidth:]) for i in range (4)]
    we_i = Signal(intbv(0))

    @always(clk.posedge, rst_n.negedge)
    def fsm():
        if not rst_n:
            state.next = t_State.IDLE
            ack.next = 0 
            Warrior.next = 0
            draw.next = True
        elif clk:
            if state == t_State.IDLE:
                ack.next = False
                if req:
                    state.next = t_State.LOAD
                    Warrior.next = 0
                    req_load.next = True

            elif state == t_State.LOAD:
                req_load.next = False

                # Here, we should do something about incrementing Warrior

                if Warrior + 1 == nbWarriors:
                    if ack_load:
                        state.next = t_State.FETCH

            elif state == t_State.FETCH:

                # Increment the Current Warrior
                if Warrior + 1 == nbWarriors:
                    # We rounded: Increment the time, and start from 0 again
                    Warrior.next = 0
                    Time.next = Time + 1
                else:
                    Warrior.next = Warrior + 1

                if Warrior.next == prevWarrior:
                    # Only one Warrior left, he won !
                    Winner.next = prevWarrior
                    state.next = t_State.IDLE
                    ack.next = True
                elif not empty_i:
                    # Current Warrior still has Task(s)
                    draw.next = False
                    state.next = t_State.PROC
                    Instr_i.next = RData
                    req_proc.next = True
            elif state == t_State.PROC:
                req_proc.next = False
                if ack_proc:
                    if Time < maxTime:
                        t_State.next = t_State.FETCH
                    else:
                        print "Time is over"
                        state.next = IDLE
                        draw.next = True
                        ack.next = True
                        
    @always(state)
    def ctrl():
        if state == t_State.IDLE:
            pass
        elif state == t_State.FETCH:
            prevWarrior.next = Warrior
        elif state == t_State.PROC:
            pass

    @always_comb
    def updateval():
        """ At loading time, we have different input than at processing time. """
        IP1_i.next = IP1_proc
        we1_i.next = we1_proc
        WData_i.next = Dout_proc
        if state == t_State.LOAD:
            IP1_i.next = IP1_load
            we1_i.next = we1_load
            WData_i.next = Dout_load

    Proc_i = Proc(Instr=Instr_i, PC=PC_i, IPOut1=IP1_proc, we1=we1_proc, IPOut2=IP2_i, we2=we2_i, WOfs=WOfs_i, WData=Dout_proc, we=we_i, ROfs=ROfs, RData=RData_i, clk=clk, rst_n=rst_n, req=req_proc, ack=ack_proc)

    Loader_i = Loader(RX_load, Warrior, we1_load, Dout_load, we1_load, IP1_load, clk, rst_n, req_load, ack_load, 9600)
    Core_i = Core(pc=PC_i, WOfs=WOfs_i, din=WData_i, ROfs=ROfs, dout=RData_i, we=we_i, clk=clk, rst_n=rst_n, maxSize=CORESIZE)

    Queue_i = TaskQueue(Warrior=Warrior,IPin1=IP1_i, IPin2=IP2_i, IPout=PC_i, re=re_i, we1=we1_i, we2=we2_i, empty=empty_i, clk=clk, rst_n=rst_n, maxWarriors=nbWarriors)
     
    return Proc_i, Loader_i, Core_i, Queue_i, fsm, ctrl, updateval

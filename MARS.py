
from myhdl import *

import MARSparam
from MARSparam import *

from Proc import Proc
from Core import Core
from Task import TaskQueue

InstrEmpty = Instr(t_OpCode.DAT, t_Modifier.F, t_Mode.DIRECT, Addr(), t_Mode.DIRECT, Addr())

def MARS(clk, rst_n, req, ack, draw, Winner, nbWarriors, maxTime):
    """ MARS is the reunion of the modules """  

    t_State=enum("IDLE", "LOAD", "FETCH", "PROC")

    state = Signal(t_State.IDLE)
    lastWarrior, Warrior = [Signal(intbv(0, min=0, max=nbWarriors)) for i in range(2)]
    Time = Signal(intbv(0, min=0, max=maxTime))

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

                if Warrior + 1 == nbWarriors:
                    if ack_load:
                        state.next = t_State.FETCH

            elif state == t_State.FETCH:

                if Warrior + 1 == nbWarriors:
                    Warrior.next = 0
                    Time.next = Time + 1
                else:
                    Warrior.next = Warrior + 1

                if Warrior.next == lastWarrior:
                    Winner.next = lastWarrior
                    state.next = t_State.IDLE
                    ack.next = True
                elif not empty_i:
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
            lastWarrior.next = Warrior
        elif state == t_Stat.PROC:
            pass

    @always_comb
    def updatewe1():
        if state == t_State.LOAD:
            we1_i.next = we1_load
        else:
            we1_i.next = we1_proc

    @always_comb
    def updateIP1():
        if state == t_State.LOAD:
            IP1_i.next = IP1_load
        else:
            IP1_i.next = IP1_proc


    PC_i, IP1_proc, IP1_i, IP2_i, WOfs_i, ROfs = [Signal(Addr()) for i in range (7)]
    we1_i, we1_load, we1_proc, we2_i, req_proc, ack_proc, re_i, empty_i = [Signal(bool()) for i in range(8)]
    Instr_i = Signal(Instr())
    WData_i, RData_i = [Signal(intbv(InstrEmpty)) for i in range (2)]
    we_i = Signal(intbv(0))

    Proc_i = Proc(Instr=Instr_i, PC=PC_i, IPOut1=IP1_proc, we1=we1_proc, IPOut2=IP2_i, we2=we2_i, WOfs=WOfs_i, WData=WData_i, we=we_i, ROfs=ROfs, RData=RData_i, clk=clk, rst_n=rst_n, req=req_proc, ack=ack_proc)
    
    Core_i = Core(pc=PC_i, WOfs=WOfs_i, din=WData_i, ROfs=ROfs, dout=RData_i, we=we_i, clk=clk, rst_n=rst_n, maxSize=CORESIZE)

    Queue_i = TaskQueue(Warrior=Warrior,IPin1=IP1_i, IPin2=IP2_i, IPout=PC_i, re=re_i, we1=we1_i, we2=we2_i, empty=empty_i, clk=clk, rst_n=rst_n, maxWarriors=nbWarriors)
     
    return Proc_i, Core_i, Queue_i, fsm, ctrl, updatewe1, updateIP1

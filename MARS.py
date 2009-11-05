
from myhdl import *

import MARSparam
from MARSparam import *

from Proc import Proc
from Core import Core
from Task import TaskQueue

InstrEmpty = Instr(t_OpCode.DAT, t_Modifier.F, t_Mode.DIRECT, Addr(), t_Mode.DIRECT, Addr())

def MARS(clk, rst_n, req, ack, draw, Winner, nbWarriors, maxTime):
    """ MARS is the reunion of the modules """  

    t_State=enum("IDLE", "FETCH", "PROC")

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

#    @always(state, ROfs_proc)
#    def updateROfs():
#        if state == t_State.FETCH:
#            ROfs.next = 0
#        else:
#            ROfs.next = ROfs_proc

    PC_i, IPOut1_i, IPOut2_i, WOfs_i, ROfs_proc, ROfs = [Signal(Addr()) for i in range (6)]
    we1_i, we2_i, req_proc, ack_proc, re_i, empty_i = [Signal(bool()) for i in range(6)]
    Instr_i = Signal(Instr())
    WData_i, RData_i = [Signal(intbv(InstrEmpty)) for i in range (2)]
    we_i = Signal(intbv(0))

    Proc_i = Proc(Instr_i, PC_i, IPOut1_i, we1_i, IPOut2_i, we2_i, WOfs_i, WData_i, we_i, ROfs, RData_i, clk, rst_n, req_proc, ack_proc)
    
    Core_i = Core(pc=PC_i, WOfs=WOfs_i, din=WData_i, ROfs=ROfs, dout=RData_i, we=we_i, clk=clk, rst_n=rst_n, maxSize=CORESIZE)

    Queue_i = TaskQueue(Warrior=Warrior,IPin1=IPOut1_i, IPin2=IPOut2_i, IPout=PC_i, re=re_i, we1=we1_i, we2=we2_i, empty=empty_i, clk=clk, rst_n=rst_n, maxWarriors=nbWarriors)
     
    return Proc_i, Core_i, Queue_i, fsm, ctrl#, updateROfs
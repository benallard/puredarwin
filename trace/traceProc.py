

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from myhdl import *

from puredarwin import MARSparam
from puredarwin.MARSparam import *

from random import randrange

from puredarwin.Proc import Proc


Core = {}
Queue = []

def init(Imp=False, Dwarf=False, Gemini=False, Mice=False, Paperone=False, Offset=0, Start=0):

    if Imp:
        Core[Offset] = Instr(t_OpCode.MOV, t_Modifier.I, t_Mode.DIRECT, Addr(), t_Mode.DIRECT, Addr(1))
    if Dwarf:
        Core[Offset] = Instr(t_OpCode.ADD, t_Modifier.AB, t_Mode.IMMEDIATE, Addr(4),t_Mode.DIRECT, Addr(3))
        Core[Offset + 1] = Instr(t_OpCode.MOV, t_Modifier.I, t_Mode.DIRECT, Addr(2), t_Mode.B_INDIRECT, Addr(2))
        Core[Offset + 2] = Instr(t_OpCode.JMP, t_Modifier.B, t_Mode.DIRECT, Addr(-2), t_Mode.DIRECT, Addr())
    if Gemini:
        Start = 2
        Core[Offset] = Instr(t_OpCode.DAT, t_Modifier.F, t_Mode.IMMEDIATE, Addr(), t_Mode.DIRECT, Addr())
        Core[Offset + 1] = Instr(t_OpCode.DAT, t_Modifier.F, t_Mode.IMMEDIATE, Addr(), t_Mode.DIRECT, Addr(99))
        Core[Offset + 2] = Instr(t_OpCode.MOV, t_Modifier.I, t_Mode.B_INDIRECT, Addr(-2), t_Mode.B_INDIRECT, Addr(-1))
        Core[Offset + 3] = Instr(t_OpCode.SNE, t_Modifier.B, t_Mode.DIRECT, Addr(-3), t_Mode.IMMEDIATE, Addr(9))
        Core[Offset + 4] = Instr(t_OpCode.JMP, t_Modifier.B, t_Mode.DIRECT, Addr(4), t_Mode.DIRECT, Addr(3))
        Core[Offset + 5] = Instr(t_OpCode.ADD, t_Modifier.AB, t_Mode.IMMEDIATE, Addr(1), t_Mode.DIRECT, Addr(-5))
        Core[Offset + 6] = Instr(t_OpCode.ADD, t_Modifier.AB, t_Mode.IMMEDIATE, Addr(1), t_Mode.DIRECT, Addr(-5))
        Core[Offset + 7] = Instr(t_OpCode.JMP, t_Modifier.B, t_Mode.DIRECT, Addr(-5), t_Mode.DIRECT, Addr(0))
        Core[Offset + 8] = Instr(t_OpCode.MOV, t_Modifier.AB, t_Mode.IMMEDIATE, Addr(99), t_Mode.DIRECT, Addr(93))
        Core[Offset + 9] = Instr(t_OpCode.JMP, t_Modifier.B, t_Mode.DIRECT, Addr(93), t_Mode.DIRECT, Addr(0))
    if Mice:
        Core[Offset] = Instr(t_OpCode.MOV, t_Modifier.AB, t_Mode.IMMEDIATE, Addr(12), t_Mode.DIRECT, Addr(-1))
        Core[Offset + 1] = Instr(t_OpCode.MOV, t_Modifier.I, t_Mode.B_INDIRECT, Addr(-2), t_Mode.B_DECREMENT, Addr(5))
        Core[Offset + 2] = Instr(t_OpCode.DJN, t_Modifier.B, t_Mode.DIRECT, Addr(-1), t_Mode.DIRECT, Addr(-3))
        Core[Offset + 3] = Instr(t_OpCode.SPL, t_Modifier.B, t_Mode.B_INDIRECT, Addr(3), t_Mode.DIRECT, Addr())
        Core[Offset + 4] = Instr(t_OpCode.ADD, t_Modifier.AB, t_Mode.IMMEDIATE, Addr(653), t_Mode.DIRECT, Addr(2))
        Core[Offset + 5] = Instr(t_OpCode.JMZ, t_Modifier.B, t_Mode.DIRECT, Addr(-5), t_Mode.DIRECT, Addr(-6))
        Core[Offset + 6] = Instr(t_OpCode.DAT, t_Modifier.F, t_Mode.IMMEDIATE, Addr(), t_Mode.IMMEDIATE, Addr(833))
    if Paperone:
        Core[Offset] = Instr(t_OpCode.SPL, t_Modifier.B, t_Mode.DIRECT, Addr(1), t_Mode.B_DECREMENT, Addr(300))
        Core[Offset + 1] = Instr(t_OpCode.SPL, t_Modifier.B, t_Mode.DIRECT, Addr(1), t_Mode.B_DECREMENT, Addr(150))
        Core[Offset + 2] = Instr(t_OpCode.MOV, t_Modifier.I, t_Mode.DIRECT, Addr(-1), t_Mode.DIRECT, Addr())
        Core[Offset + 3] = Instr(t_OpCode.SPL, t_Modifier.B, t_Mode.DIRECT, Addr(3620), t_Mode.IMMEDIATE, Addr())
        Core[Offset + 4] = Instr(t_OpCode.MOV, t_Modifier.I, t_Mode.B_INCREMENT, Addr(-1), t_Mode.A_INCREMENT, Addr(-1))
        Core[Offset + 5] = Instr(t_OpCode.MOV, t_Modifier.I, t_Mode.DIRECT, Addr(4), t_Mode.B_INCREMENT, Addr(2005))
        Core[Offset + 6] = Instr(t_OpCode.MOV, t_Modifier.I, t_Mode.DIRECT, Addr(3), t_Mode.A_INCREMENT, Addr(2042))
        Core[Offset + 7] = Instr(t_OpCode.ADD, t_Modifier.A, t_Mode.IMMEDIATE, Addr(50), t_Mode.DIRECT, Addr(-4))
        Core[Offset + 8] = Instr(t_OpCode.JMP, t_Modifier.B, t_Mode.DIRECT, Addr(-5), t_Mode.B_DECREMENT, Addr(-5))
        Core[Offset + 9] = Instr(t_OpCode.DAT, t_Modifier.F, t_Mode.B_INCREMENT, Addr(2667), t_Mode.B_INCREMENT, Addr(-2666))


    Queue.insert(0, Offset + Start)

def traceBench():
    """ How does the proc reacts to a basic IMP """

    @instance
    def WriteCore():
        while True:
            yield clk_i.posedge
            if we_i:
                Offs = int(WOfs_i)
                Addr = (PC_i + Offs) % CORESIZE
                if we_i != MARSparam.we.Full:
                    Dest = Instr(val=Core.get(Addr,InstrEmpty))
                    Src = Instr(val=int(WData_i))
                    if we_i & MARSparam.we.OpCode:
                        Dest.OpCode = Src.OpCode
                    if we_i & MARSparam.we.Modif:
                         Dest.Modifier = Src.Modifier
                    if we_i & MARSparam.we.AMod:
                         Dest.AMode = Src.AMode
                    if we_i & MARSparam.we.ANum:
                         Dest.ANumber = Src.ANumber
                    if we_i & MARSparam.we.BMod:
                         Dest.BMode = Src.BMode
                    if we_i & MARSparam.we.BNum:
                        Dest.BNumber = Src.BNumber
                    Core[Addr] = Dest
                else:
                    Core[Addr] = int(WData_i)
                print "*-->\t%s\t@ %s (%s)" % (Instr(val=Core[Addr]), Addr, bin(we_i))

    @instance
    def ReadCore():
        while True:
            yield ROfs_i, PC_i
            Offs = int(ROfs_i)
            Addr = (PC_i + Offs) % CORESIZE
            try:
                RData_i.next = Core[Addr]
                print "<--*\t@ %s\t\t%s" % (Addr, Instr(val=Core[Addr]))
            except KeyError:
                RData_i.next = InstrEmpty
                print "<--*\t@ %s\t\t..." % (Addr)

    @instance
    def WriteQueue():
        while True:
            yield clk_i.posedge
            if we1_i != 0:
                Queue.insert(0, IPOut1_i.val)
                print "+1 (%d)" % len(Queue)
                if we2_i:
                    Queue.insert(0, IPOut2_i.val)
                    print "+1 (%d)" % len(Queue)

    @instance
    def ReadQueue():
        while True:
            yield clk_i.posedge
            if re_i:
                Addr = Queue.pop()
                print "-1 (%d)" % len(Queue)
                if PC_i == Addr:
                    # I had a trouble there when RData was not updates if PC does not change
                    RData_i.next = Core.get((int(ROfs_i) + PC_i) % CORESIZE, InstrEmpty)
                PC_i.next = Addr
                print  "PC: %s" % Addr

    @instance
    def test():
        rst_n_i.next = True
        yield delay(2)
        rst_n_i.next = False #reset !
        yield delay(2)
        rst_n_i.next = True
        # run

        for i in range (700):

            clk_i.next = False
            yield delay(5)

            # do something
            req_i.next = False
            re_i.next = True
            ROfs_i.next = 0

            clk_i.next = True
            yield delay(5)
            # check

            clk_i.next = False
            yield delay(5)

            # do
            Instr_i.next = RData_i
            req_i.next = True
            re_i.next = False

            clk_i.next = True
            yield delay(5)

            while not ack_i:
                clk_i.next = False
                yield delay(5)
                req_i.next = False

                clk_i.next = True
                yield delay(5)

        raise StopSimulation

    PC_i, IPOut1_i, IPOut2_i, WOfs_i, ROfs_i = [Signal(Addr()) for i in range (5)]
    we1_i, we2_i, clk_i, rst_n_i, req_i, ack_i, re_i = [Signal(bool()) for i in range(7)]
    Instr_i = Signal(Instr())
    WData_i, RData_i = [Signal(intbv(InstrEmpty)) for i in range (2)]
    we_i = Signal(intbv(0)[MARSparam.we.WIDTH:])

    dut = Proc(Instr_i, PC_i, IPOut1_i, we1_i, IPOut2_i, we2_i, WOfs_i, WData_i, we_i, ROfs_i, RData_i, clk_i, rst_n_i, req_i, ack_i)

    return dut, test, ReadCore, WriteCore, ReadQueue, WriteQueue

if __name__ == "__main__":
    init(Gemini=True)
    tb = traceSignals(traceBench)
    sim = Simulation(tb)
    sim.run(quiet=1)

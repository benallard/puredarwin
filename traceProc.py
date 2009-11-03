
from myhdl import *

import MARSparam
from MARSparam import *

from Proc import Proc

InstrEmpty = Instr(t_OpCode.DAT, t_Modifier.F, t_Mode.DIRECT, Addr(), t_Mode.DIRECT, Addr())


Core = {}
Queue = []

def init(Imp=False, Dwarf=False, Gemini=True, Offset=0, Start=0):
    
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

    Queue.insert(0, Offset + Start)

def traceBench():
    """ How does the proc reacts to a basic IMP """  

    @instance
    def WriteCore():
        while True:
            yield clk_i.posedge
            Offs = int(WOfs_i)
            Addr = (PC_i + Offs) % CORESIZE
            if we_i:
                if we_i != MARSparam.we.Full:
                    print "I'm misbehaving"
                print "> %s @ %s" % (Instr(val=int(WData_i)), Addr)
                Core[Addr] = int(WData_i)

    @instance
    def ReadCore():
        while True:
            yield ROfs_i, PC_i
            Offs = int(ROfs_i)
            Addr = (PC_i + Offs) % CORESIZE
            try:
                RData_i.next = Core.get(Addr, InstrEmpty)
                print "< @ %s: %s" % (Addr, Instr(val=Core[Addr]))
            except KeyError:
                RData_i.next = InstrEmpty
                print "< @ %s ..." % (Addr)

    @instance
    def WriteQueue():
        while True:
            yield clk_i.posedge
            if we1_i != 0:
                Queue.insert(0, IPOut1_i.val)
                if we2_i:
                    Queue.insert(0, IPOut2_i.val)

    @instance
    def ReadQueue():
        while True:
            yield clk_i.posedge
            if re_i:
                Addr = Queue.pop()
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

        for i in range (8):

            clk_i.next = False
            yield delay(5)

            # do something
            req_i.next = False
            re_i.next = True

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
    we_i = Signal(intbv(0))

    dut = Proc(Instr_i, PC_i, IPOut1_i, we1_i, IPOut2_i, we2_i, WOfs_i, WData_i, we_i, ROfs_i, RData_i, clk_i, rst_n_i, req_i, ack_i)
     
    return dut, test, ReadCore, WriteCore, ReadQueue, WriteQueue

if __name__ == "__main__":
    init()
    tb = traceSignals(traceBench)
    sim = Simulation(tb)
    sim.run(quiet=1)

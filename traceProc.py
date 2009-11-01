
from myhdl import *

import MARSparam
from MARSparam import *

from Proc import Proc

InstrEmpty = concat(t_OpCode.DAT, t_Modifier.F, t_Mode.DIRECT, Addr(), t_Mode.DIRECT, Addr())
InstrIMP   = concat(t_OpCode.MOV, t_Modifier.I, t_Mode.DIRECT, Addr(), t_Mode.DIRECT, Addr(1))

def traceBench(IMP=False, DWARF=True):
    """ How does the proc reacts to a basic IMP """
    
    Offset = 4738

    Core = {}
    if IMP:
        Core[Offset] = InstrIMP
    if DWARF:
        Core[Offset] = Instr(t_OpCode.ADD, t_Modifier.AB, t_Mode.IMMEDIATE, Addr(4),t_Mode.DIRECT, Addr(3))
        Core[Offset + 1] = Instr(t_OpCode.MOV, t_Modifier.I, t_Mode.DIRECT, Addr(2), t_Mode.B_INDIRECT, Addr(2))
        Core[Offset + 2] = Instr(t_OpCode.JMP, t_Modifier.B, t_Mode.DIRECT, Addr(-2), t_Mode.DIRECT, Addr())
    
    @instance
    def WriteCore():
        while True:
            yield clk_i.posedge
            if we_i:
                if we_i != MARSparam.we.Full:
                    print "I'm misbehaving"
                print "> %s @ %s" % (WData_i, (PC_i + int(WOfs_i)) % CORESIZE)
                Core[(PC_i + int(WOfs_i)) % CORESIZE] = WData_i

    @instance
    def ReadCore():
        while True:
            yield ROfs_i, PC_i
            RData_i.next = Core.get((int(ROfs_i) + PC_i) % CORESIZE, InstrEmpty)
            try:
                print "< @ %s: %s" % ((int(ROfs_i) + PC_i) % CORESIZE, Core[(int(ROfs_i) + PC_i) % CORESIZE])
            except KeyError:
                print "< @ %s ..." % ((int(ROfs_i) + PC_i) % CORESIZE)

    Queue = []
    Queue.insert(0, Offset)

    @instance
    def WriteQueue():
        while True:
            yield clk_i.posedge
            if not clk_i:
                raise Error
            if IPOut1_i == 0:
                print "baoum ! (%d) %s" % (len(Queue), we_i)
            if we1_i != 0:
                print "hep"
                Queue.insert(0, IPOut1_i.val)
                if we2_i:
                    Queue.insert(0, IPOut2_i.val)

    @instance
    def ReadQueue():
        while True:
            yield clk_i.posedge
            if re_i:
                Addr = Queue.pop()
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

        Instr_i.next = InstrEmpty

        for i in range (200):

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
    we_i = Signal(intbv(0))

    dut = Proc(Instr_i, PC_i, IPOut1_i, we1_i, IPOut2_i, we2_i, WOfs_i, WData_i, we_i, ROfs_i, RData_i,  clk_i, rst_n_i, req_i, ack_i)
     
    return dut, test, ReadCore, WriteCore, ReadQueue, WriteQueue

if __name__ == "__main__":
    tb = traceSignals(traceBench)
    sim = Simulation(tb)
    sim.run(quiet=1)

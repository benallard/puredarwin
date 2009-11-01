
from myhdl import *

import MARSparam
from MARSparam import *

from Proc import Proc

InstrEmpty = concat(t_OpCode.DAT, t_Modifier.F, t_Mode.DIRECT, Addr(), t_Mode.DIRECT, Addr())
InstrIMP   = concat(t_OpCode.MOV, t_Modifier.I, t_Mode.DIRECT, Addr(), t_Mode.DIRECT, Addr(1))

def testIMP():
    """ How does the proc reacts to a basic IMP """
    
    Core = {}
    Core[CORESIZE-100] = InstrIMP
    
    @instance
    def WriteCore():
        while True:
            yield clk_i.posedge
            if we_i:
                print "> %s @ %s" % (WData_i, (PC_i + int(WOfs_i)) % CORESIZE)
                Core[(PC_i + int(WOfs_i)) % CORESIZE] = WData_i

    @instance
    def ReadCore():
        while True:
            yield ROfs_i, PC_i
            RData_i.next = Core.get((int(ROfs_i) + PC_i) % CORESIZE, InstrEmpty)
            print "< @ %s: %s" % ((int(ROfs_i) + PC_i) % CORESIZE, Core[(int(ROfs_i) + PC_i) % CORESIZE])

    Queue = []
    Queue.insert(0, CORESIZE-100)

    @instance
    def WriteQueue():
        while True:
            yield clk_i.posedge
            if we1_i:
                Queue.insert(0, IPOut1_i)
                if we2_i:
                    Queue.insert(0, IPOut2_i)

    @instance
    def ReadQueue():
        while True:
            yield clk_i.posedge
            if re_i:
                PC_i.next = Queue.pop()
                print "poped, %d remaining" % len(Queue)

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
    Instr_i, WData_i, RData_i = [Signal(intbv(InstrEmpty)[InstrWidth:]) for i in range (3)]
    we_i = Signal(intbv(0))

    dut = Proc(Instr_i, PC_i, IPOut1_i, we1_i, IPOut2_i, we2_i, WOfs_i, WData_i, we_i, ROfs_i, RData_i,  clk_i, rst_n_i, req_i, ack_i)
     
    return dut, test, ReadCore, WriteCore, ReadQueue, WriteQueue

if __name__ == "__main__":
    tb = traceSignals(testIMP)
    sim = Simulation(tb)
    sim.run(quiet=1)

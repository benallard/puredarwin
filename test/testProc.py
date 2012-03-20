import unittest

from myhdl import *

import MARSparam
from MARSparam import *

from Proc import Proc

InstrEmpty = Instr(t_OpCode.DAT, t_Modifier.F, t_Mode.DIRECT, Addr(), t_Mode.DIRECT, Addr())
InstrIMP   = Instr(t_OpCode.MOV, t_Modifier.I, t_Mode.DIRECT, Addr(), t_Mode.DIRECT, Addr(1))

class testProcBasic(unittest.TestCase):

    def testIMP(self):
        """ How does the proc reacts to a basic IMP """
        
        Core = {}
        if True: # IMP
            Core[CORESIZE-100] = InstrIMP
        if False: # DWARF
            Core[CORESIZE-100] = Instr(t_OpCode.ADD, t_Modifier.AB, t_Mode.IMMEDIATE, Addr(4),t_Mode.DIRECT, Addr(3))

        def WriteCore(we, WOfs, PC, WData, clk):
            while True:
                yield clk.posedge
                if we:
                    print "> %s at %s" % (WData, (PC + int(WOfs)) % CORESIZE)
                    Core[(PC + int(WOfs)) % CORESIZE] = WData

        def ReadCore(ROfs, PC, RData):
            while True:
                yield ROfs, PC
                RData.next = Core.get((int(ROfs) + PC) % CORESIZE, InstrEmpty)
                print "< at %s: %s" % ((int(ROfs) + PC) % CORESIZE, Core[(int(ROfs) + PC) % CORESIZE])

        Queue = []
        Queue.insert(0, CORESIZE-100)

        def WriteQueue(IP1, we1, IP2, we2, clk):
            while True:
                yield clk.posedge
                if we1:
                    Queue.insert(0, IP1)
                if we2:
                    Queue.insert(0, IP2)

        def ReadQueue(re, IP, clk):
            while True:
                yield clk.posedge
                if re:
                    IP.next = Queue.pop()

        def test(PC, re, IPOut1, we1, IPOut2, we2, WOfs, WData, we, ROfs, RData, clk, rst_n, req, ack):
            rst_n.next = True
            yield delay(2)
            rst_n.next = False #reset !
            yield delay(2)
            rst_n.next = True
            # run

            print "%s %s %s %s %s %s %s %s" % (IPOut1, we1, IPOut2, we2, WOfs, WData, we, ROfs)
            for i in range (200):
                clk.next = False
                yield delay(5)
                # set 
                re.next = True
                req.next = True

                clk.next = True
                yield delay(5)

                req.next = False
                re.next = False
                while not ack:
                    clk.next = False
                    yield delay(5)
                    # EvalOpA processed

                    print "Inter: %s %s %s %s %s %s %s %s" % (IPOut1, we1, IPOut2, we2, WOfs, WData, we, ROfs)
                
                    clk.next = True
                    yield delay(5)

                
                print "Final: %s %s %s %s %s %s %s %s" % (IPOut1, we1, IPOut2, we2, WOfs, WData, we, ROfs)
                
                # check
                self.assertEquals(IPOut1, (PC + 1) % CORESIZE)
                self.assertEquals(we1, False)
                self.assertEquals(we2, False)
                self.assertEquals(WOfs, 1)
                self.assertEquals(Core[(PC+1) % CORESIZE], InstrIMP)
                self.assertEquals(WData, InstrIMP)
            raise StopSimulation

        def run(Instr):

            PC_i, IPOut1_i, IPOut2_i, WOfs_i, ROfs_i = [Signal(Addr()) for i in range (5)]
            we1_i, we2_i, clk_i, rst_n_i, req_i, ack_i, re_i = [Signal(bool()) for i in range(7)]
            WData_i, RData_i = [Signal(intbv(0)[InstrWidth:]) for i in range (2)]
            we_i = Signal(intbv(0))

            dut = Proc(Instr, PC_i, IPOut1_i, we1_i, IPOut2_i, we2_i, WOfs_i, WData_i, we_i, ROfs_i, RData_i,  clk_i, rst_n_i, req_i, ack_i)
            check = test(PC_i, re_i, IPOut1_i, we1_i, IPOut2_i, we2_i, WOfs_i, WData_i, we_i, ROfs_i, RData_i, clk_i, rst_n_i, req_i, ack_i)
     
            writeC = WriteCore(we_i, WOfs_i, PC_i, WData_i, clk_i)
            readC = ReadCore(ROfs_i, PC_i, RData_i)

            writeQ = WriteQueue(IPOut1_i, we1_i, IPOut2_i, we2_i, clk_i)
            readQ = ReadQueue(re_i, PC_i, clk_i)

            sim = Simulation(dut, check, writeC, readC, writeQ, readQ)
            sim.run(quiet=1)

        run(InstrIMP)

if __name__ == "__main__":
    unittest.main()

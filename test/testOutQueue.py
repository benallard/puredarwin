import unittest
from unittest import TestCase

from random import randrange

from myhdl import *

from puredarwin.Proc import OutQueue

from puredarwin import MARSparam
from puredarwin.MARSparam import t_OpCode, t_Modifier

class testOutQueueProperties(TestCase):

    def testMOV(self):
        """ Test that our DUT reacts good to MOV """

        def test(PC, IPOut1, we1, we2, clk):
            for i in range(MARSparam.CORESIZE):
                clk.next = False
                yield delay(5)
                #do
                Addr = i
                PC.next = Addr

                clk.next = True
                yield delay(5)
                #test
                self.assertEquals(we1, True)
                self.assertEquals(we2, False)
                self.assertEquals(IPOut1, (Addr + 1) % MARSparam.CORESIZE)

        PC_i, IPOut1_i, IPOut2_i = [Signal(intbv()) for i in range(3)]
        we1_i, we2_i, clk_i = [Signal(bool()) for i in range(3)]

        dut = OutQueue(OpCode=t_OpCode.MOV,Modifier=0, IRA=0, IRB=0, RPA=0, PC=PC_i, IPout1=IPOut1_i, we1=we1_i, IPout2=IPOut2_i, we2=we2_i, clk=clk_i)
        check = test(PC_i, IPOut1_i, we1_i, we2_i, clk_i)

        sim = Simulation(dut, check)
        sim.run(quiet=1)

    def testDAT(self):
        """ If no we are set during DAT """

        def test(RPA, PC, we1, we2, clk):
            for i in range (10):
                clk.next = False
                yield delay(5)
                # do
                RPA = randrange(MARSparam.CORESIZE)
                PC = randrange(MARSparam.CORESIZE)
                clk.next = True
                yield delay(5)
                self.assertEquals(we1, False)
                self.assertEquals(we2, False)

        RPA_i, PC_i, IPOut1_i, IPOut2_i = [Signal(intbv(0)) for i in range(4)]
        we1_i, we2_i, clk_i = [Signal(bool()) for i in range(3)]

        dut = OutQueue(OpCode=t_OpCode.DAT, Modifier=0, IRA=0, IRB=0, RPA=RPA_i, PC=PC_i, IPout1=IPOut1_i, we1=we1_i, IPout2=IPOut2_i, we2=we2_i, clk=clk_i)
        check = test(RPA_i, PC_i, we1_i, we2_i, clk_i)

        sim = Simulation(dut, check)
        sim.run(quiet=1)

    def testSPL(self):
        """ If both Addr are set for SPL """

        def test(RPA, PC, IPOut1, we1, IPOut2, we2, clk):
            for pc in range(MARSparam.CORESIZE-100, MARSparam.CORESIZE + 100):
                clk.next = False
                yield delay(5)
                #do
                Addr = randrange(MARSparam.CORESIZE)
                RPA.next = Addr
                PC.next = pc % MARSparam.CORESIZE

                clk.next = True
                yield delay(5)
                #check
                self.assertEquals(we1, True)
                self.assertEquals(we2, True)
                self.assertEquals(IPOut1, (pc + 1) % MARSparam.CORESIZE)
                self.assertEquals(IPOut2, (pc + Addr) % MARSparam.CORESIZE)

        RPA_i, PC_i, IPOut1_i, IPOut2_i = [Signal(intbv()) for i in range(4)]
        we1_i, we2_i, clk_i = [Signal(bool()) for i in range(3)]

        dut = OutQueue(OpCode=t_OpCode.SPL, Modifier=0, IRA=0, IRB=0, RPA=RPA_i, PC=PC_i, IPout1=IPOut1_i, we1=we1_i, IPout2=IPOut2_i, we2=we2_i, clk=clk_i)
        check = test(RPA_i, PC_i, IPOut1_i, we1_i,IPOut2_i, we2_i, clk_i)

        sim = Simulation(dut, check)
        sim.run(quiet=1)

if __name__ == "__main__":
    unittest.main()

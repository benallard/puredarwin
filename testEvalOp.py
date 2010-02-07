import unittest
from unittest import TestCase
from random import randrange

from myhdl import Signal, intbv, Simulation, delay, traceSignals, StopSimulation

from Proc import EvalOp

import MARSparam
from MARSparam import InstrWidth
class testEvalOpProperties(TestCase):

    def testAll(self):
        """ Global mapping """

        clkperiod = 10 #ns

        def clkDrv(clk):
            while True:
                yield delay(clkperiod // 2)
                clk.next = not clk

        def test(req, ack, Mod, Number, Ptr, Wdata, we, Rdata, clk):
            for index in range(200):
                #set
                req.next = True
                Mod.next =index % 8
                num = randrange(MARSparam.CORESIZE)
                Number.next = num
                read = intbv(randrange(2**MARSparam.InstrWidth))
                Rdata.next = read

                # Wait for the computation to be done
                yield ack.posedge
                #check
                self.assertEquals(we | intbv("000101"), intbv("000101"))
                self.assert_(Ptr >= 0, "Ptr: %d" % Ptr)
                self.assert_(Ptr < 2*MARSparam.CORESIZE+ 1, "Ptr: %d" % Ptr)
                val = [0, num,
                       read[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + num,
                       read[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + num - 1,
                       read[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + num + 1,
                       read[MARSparam.AddrWidth:0] + num,
                       read[MARSparam.AddrWidth:0] + num - 1,
                       read[MARSparam.AddrWidth:0] + num + 1]
                self.assertEquals(Ptr, val[int(Mod)] % MARSparam.CORESIZE)
                req.next = False
                # Go back to IDLE
                yield ack.negedge
            raise StopSimulation

        Mod_i = Signal(0)
        Number_i, Ptr_i = [Signal(0) for i in range(2)]
        WData_i, RData_i = [Signal(0) for i in range(2)]
        we_i = Signal(0)
        clk_i = Signal(0)
        rst_n_i = Signal(bool(True))
        req_i, ack_i = [Signal(bool()) for i in range(2)]

        dut = EvalOp(Mod=Mod_i, Number=Number_i, Ptr=Ptr_i, WData=WData_i, we=we_i, ROfs=Signal(intbv()), RData=RData_i, clk=clk_i, rst_n=rst_n_i, req=req_i, ack=ack_i)
        check = test(req_i, ack_i, Mod_i, Number_i, Ptr_i, WData_i, we_i, RData_i, clk_i)
        clock = clkDrv(clk_i)

        sim = Simulation(dut, check, clock)
        sim.run(quiet = 1)

if __name__ == "__main__":
    unittest.main();

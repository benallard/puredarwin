import unittest
from unittest import TestCase
from random import randrange

from myhdl import Signal, intbv, Simulation, delay, traceSignals, StopSimulation

from Core import Core

import MARSparam

class testCoreProperties(TestCase):

    def testMapping(self):
        """ Global mapping """

        def ClkDrv(clk):
            clk.next = False
            while True:
                clk.next = not clk
                yield delay(10)

        def test(addr, din, dout, we):
            data = [randrange(2**MARSparam.InstrWidth) for i in range(3)]
            we.next = 0x3F
            addr0 = randrange(MARSparam.CORESIZE)
            # write three value
            addr.next = addr0
            yield delay(10)
            self.assertEqual(dout, 0)
            for i in range(3):
                print "w%d" % i
                din.next = data[i]
                yield delay(20)
                self.assertEqual(we, 0x3F)
                self.assertEqual(dout, data[i])
                addr.next = addr + 1
            we.next = 0
            addr.next = addr - 2
            yield delay(1)
            self.assertEqual(addr, addr0)
            #read them back, should be asynchronous
            for i in range(3):
                print "r%d" % i
                yield delay(4)
                addr.next = addr + 1
                self.assertEqual(dout, data[i])
            raise StopSimulation

            
                
        
        addr_i = Signal(intbv(0))
        din_i = Signal(intbv())
        dout_i = Signal(intbv(0))
        we_i = Signal(intbv(0)[6:])
        clk_i = Signal(bool(False))
        rst_n_i = Signal(bool(True))

        dut = Core(addr_i, din_i, dout_i, we_i, clk_i, rst_n_i, MARSparam.CORESIZE)
        check = test(addr_i, din_i, dout_i, we_i)
        clkdrv = ClkDrv(clk_i)

        sim = Simulation(dut, check, clkdrv)
        sim.run(quiet = 1)

if __name__ == "__main__":
    unittest.main();

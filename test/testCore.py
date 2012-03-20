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

        def test(waddr, raddr, din, dout, we):
            data = [randrange(2**MARSparam.InstrWidth) for i in range(3)]
            we.next = 0x3F
            addr0 = randrange(MARSparam.CORESIZE)
            # write three value
            waddr.next = addr0
            raddr.next = addr0
            yield delay(10)
            self.assertEqual(dout, 0)
            for i in range(3):
                din.next = data[i]
                yield delay(20)
                print "w%d" % i
                self.assertEqual(we, 0x3F)
                self.assertEqual(dout, data[i])
                waddr.next = waddr + 1
                raddr.next = raddr + 1
            we.next = 0
            waddr.next = waddr - 2
            raddr.next = addr0
            yield delay(1)
            self.assertEqual(waddr, addr0)
            #read them back, should be asynchronous
            for i in range(3):
                yield delay(4)
                print "r%d" % i
                raddr.next = raddr + 1
                self.assertEqual(raddr, addr0 + i)
                self.assertEqual(dout, data[i])
            raise StopSimulation

            
                
        
        waddr_i = Signal(intbv(0))
        raddr_i = Signal(intbv(0))
        pc_i = Signal(intbv(0))
        din_i = Signal(intbv())
        dout_i = Signal(intbv(0))
        we_i = Signal(intbv(0)[6:])
        clk_i = Signal(bool(False))
        rst_n_i = Signal(bool(True))

        dut = Core(pc_i, waddr_i, din_i, raddr_i, dout_i, we_i, clk_i, rst_n_i, MARSparam.CORESIZE)
        check = test(waddr_i, raddr_i, din_i, dout_i, we_i)
        clkdrv = ClkDrv(clk_i)

        sim = Simulation(dut, check, clkdrv)
        sim.run(quiet = 1)

if __name__ == "__main__":
    unittest.main();

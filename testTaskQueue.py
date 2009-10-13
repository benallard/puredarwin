
import unittest
from unittest import TestCase

from myhdl import Signal, intbv, Simulation, delay, traceSignals

from Task import TaskQueue

class testTaskQueueProperties(TestCase):

    def testMapping(self):

        def test(w, ipin, ipout, re, we, empty, clk, rst_n):
            rst_n.next = False
            yield delay(2)
            rst_n.next = True
            yield delay(1)

            for i in range (2):
                clk.next = False
                yield delay(10)
                w.next = i % 2
                clk.next = True
                yield delay(10)
                self.assertEqual(empty, (True, True)[i])
            print "begin"
            for i in range(10):
                print "(%d : %d)" % (i, w)
                clk.next = False
                yield delay(10)

                # dosomething
                w.next = i % 2
                ipin.next = (i+1) * 11

                re.next = (False, False, False, False, True, True, True, True, True, True)[i]
                we.next = True

                clk.next = True
                yield delay(10)

                # testsomething
                self.assertEqual(ipout, (0, 0, 0, 0, 11, 22, 33, 44, 55, 66)[i])
                self.assertEqual(empty, False)

        Warrior_i = Signal(intbv(0))
        IPin_i = Signal(intbv())
        IPout_i = Signal(intbv())
        re_i = Signal(bool())
        we_i = Signal(bool())
        empty_i = Signal(bool())
        clk_i = Signal(bool())
        rst_n_i = Signal(bool())
        dut = TaskQueue(Warrior_i, IPin_i, IPout_i, re_i, we_i, empty_i, clk_i, rst_n_i, 2)
        check = test(Warrior_i, IPin_i, IPout_i,re_i, we_i, empty_i, clk_i, rst_n_i )
        # traceSignals(test, dut)
        sim = Simulation(dut, check)
        sim.run(quiet = 1)

if __name__ == "__main__":
    unittest.main();

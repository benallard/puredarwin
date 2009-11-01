
import unittest
from unittest import TestCase

from myhdl import Signal, intbv, Simulation, delay, traceSignals

from Task import TaskQueue

class testTaskQueueProperties(TestCase):

    def testMapping(self):
        """ Global internal mapping """

        def test(w, ipin, ipout, re, we, empty, clk, rst_n):
            rst_n.next = False
            yield delay(2)
            rst_n.next = True
            yield delay(1)

            # empty at init ?
            for i in range (2):
                clk.next = False
                yield delay(10)
                w.next = i % 2
                clk.next = True
                yield delay(10)
                self.assertEqual(empty, (True, True)[i])

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
        IPin1_i, IPin2_i = [Signal(intbv()) for i in range(2)]
        IPout_i = Signal(intbv())
        re_i = Signal(bool())
        we1_i, we2_i = [Signal(bool()) for i in range(2)]
        empty_i = Signal(bool())
        clk_i = Signal(bool())
        rst_n_i = Signal(bool())

        dut = TaskQueue(Warrior=Warrior_i,
                        IPin1=IPin1_i,
                        IPin2=IPin2_i,
                        IPout=IPout_i,
                        re=re_i,
                        we1=we1_i,
                        we2=we2_i,
                        empty=empty_i,
                        clk=clk_i,
                        rst_n=rst_n_i,
                        maxWarriors=2)
        check = test(Warrior_i, IPin1_i, IPout_i,re_i, we1_i, empty_i, clk_i, rst_n_i )

        sim = Simulation(dut, check)
        sim.run(quiet = 1)

    def testDoubleWrite(self):

        def test(IPin1, IPin2, we1, we2, re, IPout, clk):

             for i in range(13):
                print "(%d)" % (i)
                clk.next = False
                yield delay(10)

                # dosomething
                IPin1.next = (i+1) * 11
                IPin2.next = (i+1) * 7

                re.next = i > 0
                we1.next =  i in (0, 1, 2, 3, 7, 8, 9, 10, 11)
                we2.next = i in (0, 1, 3, 7, 9)

                clk.next = True
                yield delay(10)

                # testsomething
                self.assertEqual(IPout, (0, 11, 7, 22, 14, 33, 44, 88, 56, 99,110,70,121)[i])

        Warrior_i = Signal(intbv(0))
        IPin1_i, IPin2_i = [Signal(intbv()) for i in range(2)]
        IPout_i = Signal(intbv())
        re_i = Signal(bool())
        we1_i, we2_i = [Signal(bool()) for i in range(2)]
        empty_i = Signal(bool())
        clk_i = Signal(bool())
        rst_n_i = Signal(bool(True))

        dut = TaskQueue(Warrior=Warrior_i,
                        IPin1=IPin1_i,
                        IPin2=IPin2_i,
                        IPout=IPout_i,
                        re=re_i,
                        we1=we1_i,
                        we2=we2_i,
                        empty=empty_i,
                        clk=clk_i,
                        rst_n=rst_n_i,
                        maxWarriors=1, maxFilling=4)
        check = test(IPin1_i,IPin2_i,we1_i, we2_i, re_i, IPout_i,clk_i)

        sim = Simulation(dut, check)
        sim.run(quiet = 1)

if __name__ == "__main__":
    unittest.main()

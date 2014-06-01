""" Run the unittest for FIFO """

import unittest
from unittest import TestCase

from myhdl import Signal, intbv, Simulation, delay

from puredarwin.Task import FIFO

class TestFIFOProperties(TestCase):

    def testEmptySet(self):
        """ test That the empty flag is set right """

        def test(re, we, empty, clk, rst_n):
            rst_n.next = False
            yield delay(2)
            rst_n.next = True
            yield delay(1)
            self.assertEqual(re,False)
            re.next = False
            we.next = False
            clk.next = True
            # empty at initialisation
            self.assertEqual(empty, True)
            yield delay(10) # posedge

            for i in range (8):
                clk.next = False
                yield delay(10)

                we.next = i in (0, 1, 6, 7)
                re.next = i in (3, 5)

                if i == 7:
                    rst_n.next = False
                    yield delay(2)
                    rst_n.next = True
                    yield delay(1)

                self.assertEqual(empty, i in (0, 6, 7))
                clk.next = True
                yield delay(10) #posedge
                self.assertEqual(empty, i == 5)

            re.next = False;

        dout_i = Signal(intbv())
        din_i = Signal(intbv())
        re_i = Signal(bool(False))
        we_i = Signal(bool(False))
        empty_i = Signal(bool())
        clk_i = Signal(bool())
        rst_n_i = Signal(bool(True))
        dut = FIFO(dout_i, din_i, we_i, 0, False, re_i, empty_i, clk_i, rst_n_i, 3)
        check = test(re_i, we_i, empty_i, clk_i, rst_n_i)
        sim = Simulation(dut, check)
        sim.run(quiet =1)

    def testNoWriteAtOverflow(self):
        """ test that further writing has no effect when full """

        def test(dout, din, re, we, empty, clk, rst_n):
            rst_n.next = False
            yield delay(2)
            rst_n.next = True
            yield delay(1)
            re.next = False # don't read
            we.next = True
            self.assertEqual(empty, True)
            for i in range (6):
                clk.next = False
                yield delay(10)
                we.next = (True, True, True, True, False, False)[i]
                re.next = (False, False, False, True, False, True)[i]
                din.next = (i+1)*11
                clk.next = True
                yield delay(10)
                self.assertEqual(dout, (None,None,None,11,11,22)[i])
            self.assertEqual(empty, True)
            re.next = False
            we.next = False


        dout_i = Signal(intbv())
        din_i = Signal(intbv())
        re_i = Signal(bool(False))
        we_i = Signal(bool(False))
        empty_i = Signal(bool())
        clk_i = Signal(bool(False))
        rst_n_i = Signal(bool(True))
        dut = FIFO(dout_i, din_i,we_i,0, False, re_i, empty_i, clk_i, rst_n_i, 2)
        check = test(dout_i, din_i, re_i, we_i, empty_i, clk_i, rst_n_i)
        sim = Simulation(dut, check)
        sim.run(quiet =1)

    def testReadWhatWeWrote(self):
        """ test were we actually check that the FIFO does not manipulate data """

        def test(dout, din, re, we, empty, clk, rst_n):
            rst_n.next = False
            yield delay(2)
            rst_n.next = True
            yield delay(1)
            re.next = False # don't read
            we.next = True
            self.assertEqual(empty, True)
            for i in range (10):
                clk.next = False
                yield delay(10)
                we.next = (True, True, True, True, True, False, True, True, False, False)[i]
                re.next = (False, True, True, True, False, True, False, True, True, False)[i]
                din.next = (i+1)*11
                clk.next = True
                yield delay(10)
                self.assertEqual(dout, (None,11,22,33,33,44,44,55, 77, 77)[i])
            re.next = False
            we.next = False


        dout_i = Signal(intbv())
        din_i = Signal(intbv())
        re_i = Signal(bool(False))
        we_i = Signal(bool(False))
        empty_i = Signal(bool())
        clk_i = Signal(bool(False))
        rst_n_i = Signal(bool(True))
        dut = FIFO(dout_i, din_i, we_i, 0, False, re_i, empty_i, clk_i, rst_n_i, 2)
        check = test(dout_i, din_i, re_i, we_i, empty_i, clk_i, rst_n_i)
        sim = Simulation(dut, check)
        sim.run(quiet =1)

if __name__ == "__main__":
    unittest.main()

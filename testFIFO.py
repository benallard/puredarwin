""" Run the unittest for FIFO """

import unittest
from unittest import TestCase

from myhdl import Signal, intbv, Simulation, delay

from Task import FIFO

class TestFIFOProperties(TestCase):

    def testEmptySet(self):
        """ test That the empty flag is set right """

        def test(re, we, empty, clk):
            self.assertEqual(re,False)
            re.next = False
            we.next = False
            clk.next = True
            yield delay(10) # posedge
            # empty at initialisation
            self.assertEqual(empty, True) # 0
            clk.next = False
            yield delay(10)
            we.next = True
            clk.next = True
            yield delay(10) #posedge
            # not empty after write
            self.assertEqual(empty, False) # 1
            clk.next = False
            yield delay(10)
            clk.next = True
            yield delay(10) #posedge
            # still not empty
            self.assertEqual(empty, False) # 2
            clk.next = False
            yield delay(10)
            we.next = False
            clk.next = True
            yield delay(10) #posedge
            self.assertEqual(empty, False) # 2
            clk.next = False
            yield delay(10)
            self.assertEqual(empty, False)
            clk.next = True
            re.next = True
            yield delay(10) # posedge
            self.assertEqual(empty, False) # 1
            clk.next = False
            yield delay(10)
            clk.next = True
            re.next = False
            yield delay(10) #posedge
            self.assertEqual(empty, False) # 1
            clk.next = False
            yield delay(10)
            clk.next = True
            re.next = True
            yield delay(10)
            self.assertEqual(empty, True) # 0
            re.next = False;
            
           
        dout_i = Signal(intbv())
        din_i = Signal(intbv())
        re_i = Signal(bool(False))
        we_i = Signal(bool(False))
        empty_i = Signal(bool())
        clk_i = Signal(bool())
        dut = FIFO(dout_i, din_i, re_i, we_i, empty_i, clk_i, 3)
        check = test(re_i, we_i, empty_i, clk_i)
        sim = Simulation(dut, check)
        sim.run(quiet =1)

if __name__ == "__main__":
    unittest.main()

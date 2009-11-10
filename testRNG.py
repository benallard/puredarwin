from myhdl import *

import unittest
from unittest import TestCase

from Loader import RNG

class testRNG(TestCase):

    def testCyclic(self):

        def test(out, clk, rst_n):

            array = []

            rst_n.next = True
            yield delay(3)
            rst_n.next = False
            yield delay(2)
            rst_n.next = True

            for i in range(5):
                clk.next = False
                yield delay(5)
                clk.next = True
                yield delay(5)
                array.insert(0, int(out))

            yield delay(3)
            rst_n.next = False
            yield delay(2)
            rst_n.next = True

            for i in range(5):
                clk.next = False
                yield delay(5)
                clk.next = True
                yield delay(5)
                self.assertEquals(out, array[4-i])

        out_i = Signal(intbv()[20:])
        clk_i, rst_n_i = [Signal(bool()) for i in range(2)]

        dut = RNG(out_i, clk_i, rst_n_i)
        check = test(out_i, clk_i, rst_n_i)

        sim = Simulation(dut, check)
        sim.run(quiet=1)

if __name__ == "__main__":
    unittest.main()

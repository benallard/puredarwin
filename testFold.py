import unittest
from unittest import TestCase
from random import randrange

from myhdl import Signal, intbv, Simulation, delay, traceSignals, StopSimulation

from Core import Fold

import MARSparam

class testFoldProperties(TestCase):

    def testAll(self):
        """ Global mapping """

        def cref(addr, limit, size):
            result = addr % limit
            if result > (limit / 2):
                result += size - limit
            return result

        def test(addrin, addrout):
            for addr in range(2 * MARSparam.CORESIZE):
                addrin.next = addr
                yield delay(5)
                self.assertEqual(addrout, cref(addrin, MARSparam.ReadRange, MARSparam.CORESIZE))
            raise StopSimulation

        addrin_i = Signal(intbv(0))
        addrout_i = Signal(intbv(0))

        dut = Fold(addrin_i, addrout_i, MARSparam.ReadRange, MARSparam.CORESIZE)
        check = test(addrin_i, addrout_i)

        sim = Simulation(dut, check)
        sim.run(quiet = 1)

if __name__ == "__main__":
    unittest.main();

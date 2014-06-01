import unittest
from unittest import TestCase
from random import randrange

from myhdl import Signal, intbv, Simulation, delay, traceSignals, StopSimulation

from puredarwin.Core import Fold

from puredarwin import MARSparam

class testFoldProperties(TestCase):

    def testAll(self):
        """ Global mapping """

        def cref(pc, addr, limit, size):
            result = addr % limit
            if result > (limit / 2):
                result += size - limit
            return (pc + result) % size

        def test(pc, addrin, addrout):
            for index in range (MARSparam.CORESIZE / 40):
                pc.next = randrange(MARSparam.CORESIZE)
                for addr in range(MARSparam.CORESIZE/40):
                    addrin.next = randrange(MARSparam.CORESIZE * 2)
                    yield delay(5)
                    self.assertEqual(addrout, cref(pc, addrin, MARSparam.ReadRange, MARSparam.CORESIZE))
            raise StopSimulation

        pc_i = Signal(intbv(0))
        addrin_i = Signal(intbv(0))
        addrout_i = Signal(intbv(0))

        dut = Fold(pc_i, addrin_i, addrout_i, MARSparam.ReadRange, MARSparam.CORESIZE)
        check = test(pc_i, addrin_i, addrout_i)

        sim = Simulation(dut, check)
        sim.run(quiet = 1)

if __name__ == "__main__":
    unittest.main()

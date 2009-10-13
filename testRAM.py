import unittest
from unittest import TestCase
from random import randrange
from myhdl import Signal, intbv, Simulation, delay, StopSimulation

from Core import RAM

class testRAMProperties(TestCase):

    def testReadAfterWrite(self):
        """ What does a Read on a adress we just wrote does ??? """

        def test(we, addr, dout, din, rst_n):

            mem = {}

            rst_n.next = False
            yield delay(2)
            rst_n.next = True
            yield delay(1)
            
            for p in range (25):
                we.next = True
                for i in range(10):
                    data = randrange(2**8)
                    address = randrange(128)
                    
                    din.next = data
                    addr.next = address
                    mem[address] = data
                    yield delay (20)
                    self.assertEqual(we, True)

                we.next = False
                for a in iter(mem):
                    addr.next = a
                    yield delay(3)
                    self.assertEqual(dout, mem[a])
            raise StopSimulation
            
        def ClkDrv(clk):
            while True:
                clk.next = not clk
                yield delay(10)

        dout_i = Signal(intbv(0))
        din_i = Signal(intbv(0))
        addr_i = Signal(intbv(0))
        we_i = Signal(bool())
        clk_i = Signal(bool())
        rst_n_i = Signal(bool(True))

        dut = RAM(dout_i, din_i, addr_i, we_i, clk_i, rst_n_i, 8, 128)
        check = test(we_i, addr_i, dout_i, din_i, we_i)
        clkdrv = ClkDrv(clk_i)

        sim = Simulation(dut, check, clkdrv)
        sim.run(quiet = 1)

if __name__ == "__main__":
    unittest.main()

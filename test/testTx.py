from myhdl import *

from random import randrange

from puredarwin.Loader import Tx, t_Parity

import unittest
from unittest import TestCase

class testTx(TestCase):
    """test our serial Transmitter"""

    def testNoParity(self):
        """ Without parity bit """

        nbBits = 8

        clkPeriod = 10 # ns
        period = int (1e9 / 115200) # 115200 baud

        def clkDrv(clk):
            while True:
                yield delay(clkPeriod // 2)
                clk.next = not clk

        def test(Rx, data, req, ack, nbBits, rst_n):
            rst_n.next = False
            yield delay(2)
            rst_n.next = True
            toreceive = intbv(val = randrange(2**nbBits))
            data.next = toreceive
            req.next = True
            for i in range(nbBits + 2):
                yield delay(period // 2)
                req.next = False
                if i == 0:
                    print "<- start"
                    self.assertEquals(Rx, False)
                    self.assertEquals(ack, False)
                elif i == nbBits + 1:
                    print "<- stop"
                    self.assertEquals(Rx, True)
                    self.assertEquals(ack, True)
                else:
                    print "<- comm"
                    self.assertEquals(Rx, toreceive[(i-1)])
                    self.assertEquals(ack, False)
                yield delay(period // 2)
            yield delay(period)
            self.assertEquals(ack, True)
            raise StopSimulation

        Tx_i, req_i, ack_i, clk_i = [Signal(bool()) for i in range(4)]
        data_i = Signal(intbv()[nbBits:])

        rst_n_i = Signal(bool())

        dut = Tx(Tx=Tx_i, data=data_i, clk=clk_i, req=req_i, ack=ack_i, rst_n=rst_n_i, nbBits=nbBits, baudrate=115200, parity=t_Parity.NO, clkrate = 1e9/clkPeriod)
        check = test(Rx = Tx_i, data=data_i, req = req_i, ack=ack_i, nbBits=nbBits, rst_n = rst_n_i)
        clock = clkDrv(clk_i)

        sim = Simulation(dut, check, clock)
        sim.run(quiet=1)

if __name__ == "__main__":
    unittest.main()

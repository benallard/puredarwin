from myhdl import *

from puredarwin.Loader import Rx, Tx, t_Parity

from random import randrange

import unittest
from unittest import TestCase

class testSerial(TestCase):
    """ Where we stick a Rx and a Tx together ... """

    def testOddParity(self):

        nbBits = 25
        clkPeriod = 10 #ns

        baudrate = 960000

        def clkDrv(clk):
            while True:
                yield delay(clkPeriod // 2)
                clk.next = not clk

        def test(rst_n, data_out, data_in, tx_req, rx_ack):
            rst_n.next = False
            yield delay(3)
            rst_n.next = True
            for i in range(25):
                tosend = intbv(val = randrange(2 ** nbBits))
                print "->\t%d" % tosend
                data_in.next = tosend
                tx_req.next = True
                yield delay(20)
                tx_req.next = False
                yield rx_ack.posedge
                received = data_out
                print "<-\t%d" % received
                self.assertEquals(received, tosend)
            raise StopSimulation


        Line_i = Signal(bool())

        clk_i, tx_req_i, tx_ack_i, rx_ack_i, rst_n_i = [Signal(bool()) for i in range(5)]

        data_in_i, data_out_i = [Signal(intbv()[nbBits:]) for i in range(2)]

        txdut = Tx(Tx=Line_i, data=data_in_i, clk=clk_i, req=tx_req_i, ack=tx_ack_i, rst_n=rst_n_i, nbBits=nbBits, baudrate=baudrate, parity=t_Parity.ODD, clkrate = 1e9/clkPeriod)
        rxdut = Rx(Rx=Line_i, data=data_out_i, clk = clk_i, ack=rx_ack_i, rst_n = rst_n_i, nbBits=nbBits, baudrate=baudrate, parity=t_Parity.ODD, clkrate=1e9/clkPeriod)
        check = test(rst_n_i, data_out_i, data_in_i, tx_req_i, rx_ack_i)
        clock = clkDrv(clk_i)

        sim = Simulation(txdut, rxdut, check, clock)
        sim.run(quiet=1)

if __name__ == "__main__":
    unittest.main()

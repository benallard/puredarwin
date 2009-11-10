from myhdl import *

from random import randrange

from Loader import Rx, t_Parity

import unittest
from unittest import TestCase

class testRx(TestCase):
    """ test our Serial Receiver """


    def testNoParity(self):
        """ Without parity bit """

        clkPeriod = 10 # ns

        period = int(1e9 / 9600000)

        def clkDrv(clk):
            while True:
                yield delay(clkPeriod//2)
                clk.next = not clk

        def test(Tx, data, ack, nbBits):
            Tx.next = True
            for i in range (20):
                yield delay(randrange(70))
                totransmit = intbv(val=randrange(2**nbBits))
                print "transmitting %d" % totransmit
                for i in range(nbBits+2):
                    yield delay(period // 2)
                    if i == 0:
                        Tx.next = False
                    elif i == nbBits+1:
                        print "stop !"
                        Tx.next = True
                    else:
                        Tx.next = totransmit[(i-1)]
                    print "setting %d: %d" % (i, Tx.next)
                    yield delay(period // 2)
                yield delay(period)
                self.assertEquals(ack, True)
                self.assertEquals(data, totransmit)
            raise StopSimulation
                    
        Rx_i, ack_i, clk_i = [Signal(bool()) for i in range(3)]
        data_i = Signal(intbv()[4:])

        dut = Rx(Rx=Rx_i, data=data_i, clk = clk_i, ack = ack_i, nbBits=4, baudrate=9600000, parity=t_Parity.NO, clkrate=1e9/clkPeriod)
        check = test(Rx_i, data_i, ack_i, 4)
        clock = clkDrv(clk_i)
        
        sim = Simulation(dut, check, clock)
        sim.run(quiet=1)



    def testOddParity(self):
        """ With Odd parity bit """

        clkPeriod = 10 # ns

        baudrate = 960000
        nbBits = 328

        period = int(1e9 / baudrate)

        def clkDrv(clk):
            while True:
                yield delay(clkPeriod//2)
                clk.next = not clk

        def test(Tx, data, ack, nbBits):
            Tx.next = True
            for i in range (5):
                yield delay(randrange(70))
                parity = True
                totransmit = intbv(val=randrange(2**nbBits))
                for i in range (nbBits):
                    if totransmit[i]:
                        parity = not parity
                print "transmitting %d" % totransmit
                for i in range(nbBits+3):
                    yield delay(period // 2)
                    if i == 0:
                        Tx.next = False
                    elif i == nbBits+1:
                        print "parity"
                        Tx.next = parity
                    elif i == nbBits+2:
                        print "stop !"
                        Tx.next = True
                    else:
                        Tx.next = totransmit[(i-1)]
                    print "setting %d: %d" % (i, Tx.next)
                    yield delay(period // 2)
                yield delay(period)
                self.assertEquals(ack, True)
                self.assertEquals(data, totransmit)
            raise StopSimulation
                    
        Rx_i, ack_i, clk_i = [Signal(bool()) for i in range(3)]
        data_i = Signal(intbv()[nbBits:])

        dut = Rx(Rx=Rx_i, data=data_i, clk = clk_i, ack = ack_i, nbBits=nbBits, baudrate=baudrate, parity=t_Parity.ODD, clkrate=1e9/clkPeriod)
        check = test(Rx_i, data_i, ack_i, nbBits)
        clock = clkDrv(clk_i)
        
        sim = Simulation(dut, check, clock)
        sim.run(quiet=1)

if __name__ == "__main__":
    unittest.main()
        

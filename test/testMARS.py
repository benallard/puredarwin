
import unittest

from myhdl import Signal, Simulation, delay

class testMARS(unittest.TestCase):
    """
    Something like:
    Two IMP always draw,
    ...

    """

    def testTwoIMP(self):

        def test(draw):
            yield delay(700)
            self.assertEquals(True, draw)


        draw_i = Signal(bool(True))

        check = test(draw_i)

        sim = Simulation(check)
        sim.run(quiet = 1)

if __name__ == "__main__":
    unittest.main()

import unittest

import myhdl

import MARSparam

class testMARSparamProperties(unittest.TestCase):

    def testAddr(self):
        """ Test the Addr class """

        Address = MARSparam.Addr(0)
        self.assert_(isinstance(Address, MARSparam.Addr))
        self.assert_(isinstance(Address, myhdl.intbv))
        self.assertEquals(len(Address), MARSparam.AddrWidth)


if __name__ == "__main__":
    unittest.main()

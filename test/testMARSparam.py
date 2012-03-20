import unittest

import myhdl

import MARSparam

class testMARSparamProperties(unittest.TestCase):

    def testAddr(self):
        """ Test the Addr class """

        Address = MARSparam.Addr()
        self.assert_(isinstance(Address, MARSparam.Addr))
        self.assert_(isinstance(Address, myhdl.intbv))
        self.assertEquals(len(Address), MARSparam.AddrWidth)

    def testInstr(self):
        """ Test the Instr class """

        Instruction = myhdl.Signal(MARSparam.Instr())
        self.assert_(isinstance(Instruction._val, myhdl.intbv))
        self.assert_(isinstance(Instruction, myhdl._Signal.Signal))
        self.assert_(isinstance(Instruction.val, MARSparam.Instr))
        self.assertEquals(len(Instruction), MARSparam.InstrWidth)
        for i in range(len(Instruction)):
            self.assertEquals(Instruction[i], 0)

        Instruction.OpCode = MARSparam.t_OpCode.SPL
        self.assertEquals(Instruction.Modifier, 0)
        self.assertEquals(len(Instruction.BNumber), MARSparam.AddrWidth)
        for i in range (5):
            self.assertEquals(Instruction[MARSparam.InstrWidth-i], MARSparam.t_OpCode.SPL[5-i])

if __name__ == "__main__":
    unittest.main()

"""
This is the processor of the MARS

We will try to keep it as quick as possible ...
"""

from myhdl import *

import MARSparam
from MARSparam import t_OpCode, t_Modifier, t_Mode
from MARSparam import InstrWidth

def EvalOp(Mod, Number, Ptr, WData, we, RData, clk):
    """
    Eval A operand (Or actually B operand)

    assumption:
    Rdata = Core[Number + IP]
    WOfs == Number


    We don'y take any reset as input as we don't keep any internal state ...

    """

    @always(clk.posedge)
    def fsm():
        we.next = 0

        if Mod == t_Mode.IMMEDIATE:
            Ptr.next = 0
        elif Mod == t_Mode.DIRECT:
            Ptr.next = Number

        elif Mod == t_Mode.A_INDIRECT:
            Ptr.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + Number
        elif Mod == t_Mode.A_INCREMENT:
            Ptr.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + Number + 1
            we.next = MARSparam.we.ANum
            WData.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + 1
        elif Mod == t_Mode.A_DECREMENT:
            Ptr.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + Number - 1
            we.next = MARSparam.we.ANum
            WData.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] - 1

        elif Mod == t_Mode.B_INDIRECT:
            Ptr.next = RData[MARSparam.AddrWidth:0] + Number
        elif Mod == t_Mode.B_INCREMENT:
            Ptr.next = RData[MARSparam.AddrWidth:0] + Number + 1
            we.next = MARSparam.we.BNum
            WData.next = RData[MARSparam.AddrWidth:0] + 1
        elif Mod == t_Mode.B_DECREMENT:
            Ptr.next = RData[MARSparam.AddrWidth:0] + Number - 1
            we.next = MARSparam.we.BNum
            WData.next = RData[MARSparam.AddrWidth:0] - 1
        else:
            raise ValueError("Mod: %d not understood" % Mod)

    return fsm

def OutQueue(OpCode, RPA, PC, IPout1, we1, IPout2, we2, clk):
    """
    The Exec part that output to the TaskQueue

    """

    @always(clk.posedge)
    def Out1():
        we1.next = True
        if OpCode == t_OpCode.DAT:
            we1.next = False
        elif OpCode in (t_OpCode.MOV,
                      t_OpCode.ADD,
                      t_OpCode.SUB,
                      t_OpCode.MUL,
                      t_OpCode.SPL,
                      t_OpCode.NOP):
            IPout1.next = (PC + 1) % MARSparam.CORESIZE
        elif OpCode == t_OpCode.JMP:
            IPOut1.next = RPA
        else:
            raise NotImplementedError("Queue: Only few OpCode are Implemented: not %s" % OpCode)

    @always(clk.posedge)
    def Out2():
        we2.next = False
        if OpCode is t_OpCode.SPL:
            IPout2.next = RPA
            we2.next = True

    return Out1, Out2

def OutCore(OpCode, Modif, IRA, IRB, we, WData, clk):
    """
    WPA is not used anymore at this stage
    RPA is only used to Queue

    RPB is not used any more at this stage
    WPB is used for every write

    assumption:
    WOfs == BPtr

    Any division by Zero is killing the current task
    """

    @always(clk.posedge)
    def comb():

        def op(OpCode, Num1, Num2):
            if OpCode == t_OpCode.ADD:
                return Num1 + Num2
            elif OpCode == t_OpCode.SUB:
                return Num1 + MARSparam.CORESIZE - Num2
            elif OpCode == t_OpCode.MUL:
                return Num1 * Num2
            elif OpCode == t_OpCode.DIV:
                return Num1 / Num2
            elif OpCode == t_OpCode.MOD:
                return Num1 % Num2
            else:
                raise ValueError("OpCode %s is not arithmetic" % OpCode)

        we.next = 0
        if OpCode in (t_OpCode.DAT,
                      t_OpCode.JMP,
                      t_OpCode.JMZ,
                      t_OpCode.JMN,
                      t_OpCode.CMP,
                      t_OpCode.SNE,
                      t_OpCode.SLT,
                      t_OpCode.SPL,
                      t_OpCode.NOP):
            # Those don't touch the Core
            pass

        elif OpCode == t_OpCode.MOV:
            if Modif == t_Modifier.A:
                WData.next = MARSparam.Instr(ANumber=IRA.Anumber)
                we.next = MARSparam.we.A
            elif Modif == t_Modifier.B:
                WData.next = MARSparam.Instr(BNumber=IRA.BNumber)
                we.next = MARSparam.we.B
            elif Modif == t_Modifier.AB:
                WData.next = MARSparam.Instr(ANumber=IRA.BNumber)
                we.next = MARSparam.we.AB
            elif Modif == t_Modifier.BA:
                WData.next = MARSparam.Instr(BNumber=IRA.Anumber)
                we.next = MARSparam.we.BA
            elif Modif == t_Modifier.F:
                WData.next = MARSparam.Instr(ANumber=IRA.ANumber,
                                             BNumber=IRA.BNumber)
                we.next = MARSparam.we.F
            elif Modif == t_Modifier.X:
                WData.next = MARSparam.Instr(ANumber=IRA.Bnumber, 
                                             BNumber=IRA.ANumber)
                we.next = MARSparam.we.X
            elif Modif == t_Modifier.I:
                WData.next = IRA
                we.next = MARSparam.we.I
            else:
                raise ValueError("Modifier %d not supported" % Modif)

        elif OpCode in (t_OpCode.ADD,
                        t_OpCode.SUB,
                        t_OpCode.MUL):
            if Modif == t_Modifier.A:
                WData.next = MARSparam.Instr(ANumber = op(OpCode, IRB.ANumber, IRA.ANumber))
                we.next = MARSparam.we.A
            else:
                raise NotImplementedError

        else:
            raise NotImplementedError("Core: Only few OpCode are implemented ; not %s" % OpCode)

    return comb

def Proc(Instr, PC, IPOut1, we1, IPOut2, we2, WOfs, WData, we, ROfs, RData, clk, rst_n, req, ack):
    """
    We have here  three state fsm: EvalA, EvalB, The rest
    Thus we have state, thus, we need a rst(_n)
    
    """

    t_State = enum("IDLE", "EVALOPA", "EVALOPB", "REST")

    state = Signal(t_State.IDLE)

    OpCode = Signal(intbv(0)[5:])
    Modifier = Signal(intbv(0)[3:])
    AMode = Signal(intbv(0)[3:])
    ANumber = Signal(MARSparam.Addr())
    BMode = Signal(intbv(0)[3:])
    BNumber = Signal(MARSparam.Addr())

    APtr, BPtr = [Signal(MARSparam.Addr()) for i in range(2)]

    IRA, IRB = [Signal(intbv(0)[MARSparam.InstrWidth:]) for i in range(2)]

    WData_evalopa, WData_evalopb, WData_outcore = [Signal(intbv(0)[MARSparam.InstrWidth:]) for i in range(3)]

    we_evalopa, we_evalopb, we_outcore = [Signal(intbv(0)[6:]) for i in range(3)]

    we1_outqueue, we2_outqueue = [Signal(bool()) for i in range(2)]

    EvalAOp = EvalOp(AMode, ANumber, APtr, WData_evalopa, we_evalopa, RData, clk)
    EvalBOp = EvalOp(BMode, BNumber, BPtr, WData_evalopb, we_evalopb, RData, clk)
    OutQueue_i = OutQueue(OpCode, APtr, PC, IPOut1, we1_outqueue, IPOut2, we2_outqueue, clk)
    OutCore_i = OutCore(OpCode, Modifier, IRA, IRB, we_outcore, WData_outcore, clk)

    @always_comb
    def link():
        OpCode.next = Instr[InstrWidth:InstrWidth-5]
        Modifier.next = Instr[InstrWidth-5:InstrWidth-8]
        AMode.next = Instr[InstrWidth-8:InstrWidth-11]
        ANumber.next = Instr[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth]
        BMode.next = Instr[MARSparam.AddrWidth+3:MARSparam.AddrWidth]
        BNumber.next = Instr[MARSparam.AddrWidth:0]

    @always(clk.posedge, rst_n.negedge)
    def fsm():
        if not rst_n:
            state.next = t_State.IDLE
        elif clk:
            print "."
            if state == t_State.IDLE:
                if req:
                    state.next = t_State.EVALOPA
                    ack.next = False
            elif state == t_State.EVALOPA:
                # we could jump to REST if evalopa and evalopb 
                # both don't write and if B is not dependant 
                # on A's output
                state.next = t_State.EVALOPB
            elif state == t_State.EVALOPB:
                state.next = t_State.REST
            elif state == t_State.REST:
                state.next = t_State.IDLE
                ack.next = True
            else:
                raise ValueError("state value not allowed: %s" % state)
            
    @always(state)
    def fsmcore():
        we.next = 0
        """
        Output Signals for the Core
        actually: a few big MUX
        """
        if state == t_State.IDLE:
            print "state is IDLE"
            we1.next = False
            we2.next = False
        elif state == t_State.EVALOPA:
            print "state is EVALA"
            we.next = we_evalopa
            WData.next = WData_evalopa
            WOfs.next = ANumber
        elif state == t_State.EVALOPB:
            print "state is EVALB"
            we.next = we_evalopb
            WData.next = WData_evalopb
            WOfs.next = BNumber
            IRA.next = RData
        elif state == t_State.REST:
            print "state is REST"
            we.next = we_outcore
            WData.next = WData_outcore
            WOfs.next = BPtr
            we1.next = we1_outqueue
            we2.next = we2_outqueue
            IRB.next = RData

    @always_comb
    def updateROfs():
        ROfs.next = APtr
        ROfs.next = BPtr
        print "%s %s %s " % (ROfs, APtr, BPtr)


    return EvalAOp, EvalBOp, OutQueue_i, OutCore_i, link, fsm, fsmcore

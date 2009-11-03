"""
This is the processor of the MARS

We will try to keep it as quick as possible ...
"""

from myhdl import *

import MARSparam
from MARSparam import t_OpCode, t_Modifier, t_Mode
from MARSparam import InstrWidth

def EvalOp(Mod, Number, Ptr, WData, we, ROfs, RData, clk, rst_n, req, ack):
    """
    Eval A operand (Or actually B operand)

    assumption:
    WOfs == Number


    """

    t_State = enum("IDLE", "COMPUTE", "READ")
    state = Signal(t_State.IDLE)

    @always(clk.posedge, rst_n)
    def fsm():
        if not rst_n:
            state.next = t_State.IDLE
        elif clk:
            if state == t_State.IDLE:
                if req:
                    state.next = t_State.COMPUTE
                    ROfs.next = Number
            elif state == t_State.COMPUTE:
                state.next = t_State.READ
                ROfs.next = Ptr
            elif state == t_State.READ:
                state.next = t_State.IDLE

    @always(state)
    def out():
        we.next = 0
        if state == t_State.COMPUTE:
            if Mod == t_Mode.IMMEDIATE:
                Ptr.next = 0
            elif Mod == t_Mode.DIRECT:
                Ptr.next = Number

            elif Mod == t_Mode.A_INDIRECT:
                Ptr.next = MARSparam.Instr(val=int(RData)).ANumber + Number
            elif Mod == t_Mode.A_INCREMENT:
                Ptr.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + Number + 1
                we.next = MARSparam.we.ANum
                WData.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + 1
            elif Mod == t_Mode.A_DECREMENT:
                Ptr.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] + Number - 1
                we.next = MARSparam.we.ANum
                WData.next = RData[InstrWidth-11:InstrWidth-11-MARSparam.AddrWidth] - 1

            elif Mod == t_Mode.B_INDIRECT:
                Ptr.next = MARSparam.Instr(val=int(RData)).BNumber + Number
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
        elif state == t_State.READ:
            ack.next = True    
        elif state == t_State.IDLE:
            ack.next = False

    return fsm, out

def OutQueue(OpCode, RPA, PC, IPout1, we1, IPout2, we2, clk):
    """
    The Exec part that output to the TaskQueue

    """

    @always(clk.posedge)
    def Out1():
        PC1 = (PC + 1) % MARSparam.CORESIZE
        PC2 = (PC + 2) % MARSparam.CORESIZE
        PCRPA = (PC + RPA) % MARSparam.CORESIZE
        we1.next = True
        if OpCode == t_OpCode.DAT:
            we1.next = False
        elif OpCode in (t_OpCode.MOV,
                        t_OpCode.ADD,
                        t_OpCode.SUB,
                        t_OpCode.MUL,
                        t_OpCode.SPL,
                        t_OpCode.NOP):
            IPout1.next = PC1
        elif OpCode == t_OpCode.JMP:
            IPout1.next = PCRPA
        elif OpCode in (t_OpCode.JMZ,
                        t_OpCode.JMN,
                        t_OpCode.DJN):

            def test(Number):
                if OpCode == t_OpCode.JMZ:
                    return Number == 0
                elif OpCode == t_OpCode.JMN:
                    return Number != 0
                elif OpCode == t_OpCode.DJN:
                    return (Number - 1) != 0

            if Modifier in (t_Modifier.A,
                            t_Modifier.BA):
                if test(IRB.ANumber):
                    IPOut1.next = PCRPA
                else:
                    IPOut1.next = PC1
            if Modifier in (t_Modifier.B,
                            t_Modifier.AB):
                if test(IRB.BNumber):
                    IPOut1.next = PCRPA
                else:
                    IPOut1.next = PC1
            if Modifier in (t_Modifier.F,
                            t_Modifier.X,
                            t_Modifier.I):
                if test(IRB.ANumber) and test(IRB.BNumber):
                    IPOut1.next = PCRPA
                else:
                    IPOut1.next = PC1

        elif OpCode == t_OpCode.CMP:
            if Modifier == t_Modifier.A:
                if IRA.ANumber == IRB.ANumber:
                    IPOut1.next = PC2
                else:
                    IPOut1.next = PC1
            elif Modifier == t_Modifier.B:
                if IRA.BNumber == IRB.BNumber:
                    IPOut1.next = PC2
                else:
                    IPOut1.next = PC1
            elif Modifier == t_Modifier.AB:
                if IRA.ANumber == IRB.BNumber:
                    IPOut1.next = PC2
                else:
                    IPOut1.next = PC1
            elif Modifier == t_Modifier.BA:
                if IRA.BNumber == IRB.ANumber:
                    IPOut1.next = PC2
                else:
                    IPOut1.next = PC1
            elif Modifier == t_Modifier.F:
                if (IRA.ANumber == IRB.ANumber) and (IRA.BNumber == IRB.BNumber):
                    IPOut1.next = PC2
                else:
                    IPOut1.next = PC1
            elif Modifier == t_Modifier.X:
                if (IRA.ANumber == IRB.BNumber) and (IRA.BNumber == IRB.ANumber):
                    IPOut1.next = PC2
                else:
                    IPOut1.next = PC1
            elif Modifier == t_Modifier.I:
                if IRA == IRB:
                    IPout1.next = PC2
                else:
                    IPOut1.next = PC1

        elif OpCode == t_OpCode.SNE:
            if Modifier == t_Modifier.A:
                if IRA.ANumber != IRB.ANumber:
                    IPOut1.next = PC2
                else:
                    IPOut1.next = PC1
            elif Modifier == t_Modifier.B:
                if IRA.BNumber != IRB.BNumber:
                    IPOut1.next = PC2
                else:
                    IPOut1.next = PC1
            elif Modifier == t_Modifier.AB:
                if IRA.ANumber != IRB.BNumber:
                    IPOut1.next = PC2
                else:
                    IPOut1.next = PC1
            elif Modifier == t_Modifier.BA:
                if IRA.BNumber != IRB.ANumber:
                    IPOut1.next = PC2
                else:
                    IPOut1.next = PC1
            elif Modifier == t_Modifier.F:
                if (IRA.ANumber != IRB.ANumber) or (IRA.BNumber != IRB.BNumber):
                    IPOut1.next = PC2
                else:
                    IPOut1.next = PC1
            elif Modifier == t_Modifier.X:
                if (IRA.ANumber != IRB.BNumber) or (IRA.BNumber != IRB.ANumber):
                    IPOut1.next = PC2
                else:
                    IPOut1.next = PC1
            elif Modifier == t_Modifier.I:
                if IRA != IRB:
                    IPout1.next = PC2
                else:
                    IPOut1.next = PC1
        else:
            raise NotImplementedError("Queue: Only few OpCode are Implemented: not %s" % OpCode)

    @always(clk.posedge)
    def Out2():
        we2.next = False
        if OpCode is t_OpCode.SPL:
            IPout2.next = (PC + RPA) % MARSparam.CORESIZE
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
                return (Num1 + Num2) % MARSparam.CORESIZE
            elif OpCode == t_OpCode.SUB:
                return (Num1 + MARSparam.CORESIZE - Num2) % MARSparam.CORESIZE
            elif OpCode == t_OpCode.MUL:
                return (Num1 * Num2)  % MARSparam.CORESIZE
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
            elif Modif == t_Modifier.B:
                WData.next = MARSparam.Instr(BNumber = op(OpCode, IRB.BNumber, IRA.BNumber))
                we.next = MARSparam.we.B
            elif Modif == t_Modifier.AB:
                WData.next = MARSparam.Instr(BNumber = op(OpCode,  IRB.BNumber, IRA.ANumber))
                print "Calculated: %s %s %s" % (IRB.BNumber, IRA.ANumber, WData.next)
                we.next = MARSparam.we.AB
            elif Modif == t_Modifier.BA:
                WData.next = MARSparam.Instr(ANumber = op(OpCode, IRB.ANumber, IRA.BNumber))
                we.next = MARSparam.we.BA
            elif Modif in (t_Modifier.F, 
                           t_Modifier.I):
                WData.next = MARSparam.Instr(ANumber = op(OpCode, IRB.ANumber, IRA.ANumber),
                                             BNumber = op(OpCode, IRB.BNumber, IRA.BNumber))
                we.next = MARSparam.we.F
            elif Modif == t_Modifier.X:
                WData.next = MARSparam.Instr(BNumber = op(OpCode, IRB.ANumber, IRA.BNumber),
                                             ANumber = op(OpCode, IRB.BNumber, IRA.ANumber))
                we.next = MARSparam.we.F
            else:
                raise ValueError(Modif)

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

    APtr, BPtr, ROfs_evalopa, ROfs_evalopb = [Signal(MARSparam.Addr()) for i in range(4)]

    IRA, IRB = [Signal(MARSparam.Instr()) for i in range(2)]

    WData_evalopa, WData_evalopb, WData_outcore = [Signal(intbv(0)[MARSparam.InstrWidth:]) for i in range(3)]

    we_evalopa, we_evalopb, we_outcore = [Signal(intbv(0)[6:]) for i in range(3)]
    
    req_evalopa, ack_evalopa, req_evalopb, ack_evalopb = [Signal(bool()) for i in range(4)]

    we1_outqueue, we2_outqueue = [Signal(bool()) for i in range(2)]

    EvalAOp = EvalOp(AMode, ANumber, APtr, WData_evalopa, we_evalopa, ROfs_evalopa, RData, clk, rst_n, req_evalopa, ack_evalopa)
    EvalBOp = EvalOp(BMode, BNumber, BPtr, WData_evalopb, we_evalopb, ROfs_evalopb, RData, clk, rst_n, req_evalopb, ack_evalopb)
    OutQueue_i = OutQueue(OpCode, APtr, PC, IPOut1, we1_outqueue, IPOut2, we2_outqueue, clk)
    OutCore_i = OutCore(OpCode, Modifier, IRA, IRB, we_outcore, WData_outcore, clk)

    @always_comb
    def link():
        OpCode.next = Instr.OpCode
        Modifier.next = Instr.Modifier
        AMode.next = Instr.AMode
        ANumber.next = Instr.ANumber
        BMode.next = Instr.BMode
        BNumber.next = Instr.BNumber
        req_evalopb.next = ack_evalopa
        req_evalopa.next = req

    @always(clk.posedge, rst_n.negedge)
    def fsm():
        if rst_n == False:
            state.next = t_State.IDLE
        elif clk:
            if state == t_State.IDLE:
                ack.next = False
                if req:
                    state.next = t_State.EVALOPA
            elif state == t_State.EVALOPA:
                # we could jump to REST if evalopa and evalopb 
                # both don't write and if B is not dependant 
                # on A's output
                if ack_evalopa:
                    state.next = t_State.EVALOPB
            elif state == t_State.EVALOPB:
                if ack_evalopb:
                    #IRB.next = MARSparam.Instr(val=int(RData))
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
            we1.next = False
            we2.next = False
        elif state == t_State.EVALOPA:
            we.next = we_evalopa
            WData.next = WData_evalopa
            WOfs.next = ANumber
        elif state == t_State.EVALOPB:
            we.next = we_evalopb
            WData.next = WData_evalopb
            WOfs.next = BNumber
            #IRA.next = MARSparam.Instr(val=int(RData))
        elif state == t_State.REST:
            we.next = we_outcore
            WData.next = WData_outcore
            WOfs.next = BPtr
            we1.next = we1_outqueue
            we2.next = we2_outqueue

    @always_comb
    def updateROfs():
        if state == t_State.EVALOPA:
            ROfs.next = ROfs_evalopa
        elif state == t_State.EVALOPB:
            ROfs.next = ROfs_evalopb
        elif state == t_State.IDLE:
            ROfs.next = 0

    @always_comb
    def updateIRX():
        if state == t_State.EVALOPB:
            IRB.next = MARSparam.Instr(val=int(RData))
        if state == t_State.EVALOPA:
            IRA.next = MARSparam.Instr(val=int(RData))


    return EvalAOp, EvalBOp, OutQueue_i, OutCore_i, link, fsm, fsmcore, updateROfs, updateIRX

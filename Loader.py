"""

Ok, let's load the warriors from a serial line,

and generate the Random position through a LFSR

"""

import MARSparam

class ASCII:
    NULL = 0x00
    SOH  = 0x01
    STX  = 0x02
    ETX  = 0x03
    EOT  = 0x04 # End of transmission
    ENQ  = 0x05
    ACK  = 0x06
    BEL  = 0x07
    BS   = 0x08
    TAB  = 0x09
    LF   = 0x0A
    VT   = 0x0B
    FF   = 0x0C
    CR   = 0x0D
    SO   = 0x0E
    SI   = 0x0F
    DLE  = 0x10
    DC1  = 0x11
    DC2  = 0x12
    DC3  = 0x13
    DC4  = 0x14
    NAK  = 0x15
    SYN  = 0x16
    ETB  = 0x17
    CAN  = 0x18
    EM   = 0x19
    SUB  = 0x1A
    ESC  = 0x1B
    FS   = 0x1C
    GS   = 0x1D
    RS   = 0x1E
    US   = 0x1F

from myhdl import *

t_Parity = enum("EVEN", "ODD", "MARK", "SPACE", "NO")

def Rx(Rx, data, clk, ack, rst_n, nbBits, baudrate, parity, clkrate):
    """
    My serial line
    """

    t_State = enum("WAIT", "DELAY", "RECEIVE")
    sampling_time =  int(clkrate / baudrate)

    state = Signal(t_State.WAIT)

    data_i = Signal(intbv(0)[nbBits:])

    bitReceived = Signal(intbv(0, min=0, max=nbBits+3))
    time = Signal(intbv(0,min=0, max=sampling_time+2))

    parity_bit = Signal(bool())
    parity_ok = Signal(bool())


    @always(clk.posedge, rst_n.negedge)
    def rx():
        if not rst_n:
            state.next = t_State.WAIT
            ack.next = False
        elif clk:
            if state == t_State.WAIT:
                parity_ok.next = False
                if Rx == False:
                    state.next = t_State.DELAY
                    bitReceived.next = 0
                    time.next = sampling_time // 2
                    if parity == t_Parity.EVEN:
                        parity_bit.next = True
                    elif parity == t_Parity.ODD:
                        parity_bit.next = False

            elif state == t_State.DELAY:
                time.next = time + 1
                if time == sampling_time:
                    time.next = 0
                    state.next = t_State.RECEIVE

            elif state == t_State.RECEIVE:
                ack.next = False
                time.next = time + 1
                if time == sampling_time-1:
                    time.next = 0
                    bitReceived.next = bitReceived + 1
                    if bitReceived == nbBits: # parity bit
                        if parity == t_Parity.NO:
                            state.next = t_State.WAIT
                            if Rx: # stop bit
                                ack.next = True
                                data.next = data_i
                                data_i.next = 0
                            else:
                                ack.next = False
                        elif parity == t_Parity.MARK:
                            if Rx:
                                parity_ok.next = True
                            else:
                                parity_ok.next = False
                        elif parity == t_Parity.SPACE:
                            if Rx:
                                parity_ok.next = False
                            else:
                                parity_ok.next = True
                        else:
                            if parity_bit == Rx:
                                parity_ok.next = True
                            else:
                                parity_ok.next = False

                    elif  bitReceived == nbBits + 1: # stop bit
                        if parity == t_Parity.NO:
                            raise Error("Shouldn't be there")
                        state.next = t_State.WAIT
                        if Rx:
                            ack.next = parity_ok
                            data.next = data_i
                            data_i.next = 0
                        else:
                            ack.next = False
                    else: # usual communication
                        parity_bit.next = parity_bit ^ Rx 
                        data_i.next = int(Rx) * (2**(nbBits-1)) +  data_i[nbBits:1]
#                        data_i.next = concat(intbv(Rx.val)[1:], data_i.val[nbBits-1:])
            

    return rx

def RNG(out, clk, rst_n):
    """
    My LFSR

    20 bits LFSR XNOR(20, 17)
    """

    @always(clk.posedge, rst_n.negedge)
    def generate():
        if not rst_n:
            out.next = 0xa9e1b
        elif clk:
            out.next = out[19:] * 2 + (out[19] ^ out[16])

    return generate

def Loader(rs232_Rx, Warrior, we, Dout, we1, IP1, clk, rst_n, req, ack, baudrate):
    """
    The loader will be called once for all Warriors, then the Warriors will be sent over RS232.
    """

    random = Signal(intbv(0)[20:])

    t_State = enum("IDLE","THINK", "RECEIVE", "WRITE")

    state = Signal(t_State.IDLE)

    @always(clk.posedge, rst_n.negedge)
    def ctrl():
        if not rst_n:
            state.next = t_State.IDLE

        elif clk:
            if state == t_State.IDLE:
                pass

            elif state == t_State.THINK:
                if Warrior != maxWarriors:
                    state.next = t_State.RECEIVE
                else:
                    state.next = IDLE

            elif state == t_State.RECEIVE:
                pass

            elif state == t_State.WRITE:
                if data_i != ASCII.EOT:
                    state.next = t_State.RECEIVE
                else:
                    state.next = t_State.THINK

    @always(state)
    def state():
        we.next = False
        we1.next = False
        if state == t_State.IDLE:
            pass
        elif state == t_State.THINK:
            we1.next = Address_i
        elif state == t_State.RECEIVE:
            pass
        elif state == t_State.WRITE:
            we.next = True
            Dout.next = data_i

    data_i = Signal(intbv(0)[MARSparam.InstrWidth:])


    RNG_i = RNG(random, clk, rst_n)
    # 1e9: ns;  10: clk @ 10 ns
    Rx_i = Rx(rs232_Rx, data_i, clk, ack, rst_n, MARSparam.InstrWidth, baudrate, t_Parity.NO, 1e9/10 )

    return ctrl, state, RNG_i, Rx_i

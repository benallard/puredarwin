"""

Ok, let's load the warriors from a serial line,

and generate the Random position through a LFSR

"""

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

    random = Signal(intbv()[20:])

    t_State = enum("IDLE","THINK", "RECEIVE", "WRITE")

    @always(clk.posedge, rst_n.negedge)
    def ctrl():
        if not rst_n:
            pass
        elif clk:
            pass

    RNG_i = RNG(random, clk, rst_n)
    Rx_i = Rx(rs232_Rx, data_i, vlk, rst_n, )

`include "mars_params.vh"


`default_nettype none

// A dumb RAM with asynchronous read
// And synchronous write
module ram(i_clk, i_raddr, o_dout, i_waddr, i_din, i_we);
    parameter WIDTH=16;
    parameter DEPTH=`CORESIZE;

    input i_clk, i_we;
    input [$clog2(DEPTH) - 1:0] i_raddr;
    output reg [WIDTH-1:0] o_dout;
    input [$clog2(DEPTH) - 1:0] i_waddr;
    input [WIDTH-1: 0] i_din;

    reg  [WIDTH-1:0] mem [0:DEPTH-1];

    always @(posedge i_clk)
    begin
        if (i_we)
    	    mem[i_waddr] <= i_din;
        o_dout = mem[i_raddr];
    end
    //assign o_dout = mem[i_raddr];

endmodule

module fold(i_pc, i_offset, o_address);
    parameter MAX_SIZE=`CORESIZE;
    parameter LIMIT=400;

    input [$clog2(MAX_SIZE)-1:0] i_pc, i_offset;
    output [$clog2(MAX_SIZE)-1:0] o_address; 

    wire [$clog2(MAX_SIZE)-1:0] ofs_fold, ofs_limit;

    assign ofs_limit = i_offset % LIMIT;

    assign ofs_fold = (ofs_limit > (LIMIT >> 1)) ? ofs_limit + MAX_SIZE - LIMIT : ofs_limit;

    assign o_address = (i_pc + ofs_fold) % MAX_SIZE;
endmodule

module core(i_clk, i_rst_n, i_pc, i_woffs, i_din, i_roffs, o_dout, i_we);
    parameter MAX_SIZE=`CORESIZE;

    input i_clk, i_rst_n;
    input [$clog2(MAX_SIZE)-1:0] i_pc, i_woffs, i_roffs;
    input [`INSTR_WIDTH-1:0] i_din;
    output [`INSTR_WIDTH-1:0] o_dout;
    input [5:0] i_we;

    wire [`ADDR_WIDTH-1:0] r_addr, w_addr;


    wire opcode_we, modif_we, amode_we, anumber_we, bmode_we, bnumber_we;

    wire [4:0] opcode_out, opcode_in;
    wire [2:0] modif_out, modif_in;
    wire [2:0] amode_out, amode_in;
    wire [$clog2(MAX_SIZE)-1:0] anumber_out, anumber_in;
    wire [2:0] bmode_out, bmode_in;
    wire [$clog2(MAX_SIZE)-1:0] bnumber_out, bnumber_in;

    assign {opcode_in, modif_in, amode_in, anumber_in, bmode_in, bnumber_in} = i_din;
    assign o_dout = {opcode_out, modif_out, amode_out, anumber_out, bmode_out, bnumber_out};

    assign {opcode_we, modif_we, amode_we, anumber_we, bmode_we, bnumber_we} = i_we;

    fold #(MAX_SIZE, `READ_RANGE) read_fold (i_pc, i_roffs, r_addr);
    fold #(MAX_SIZE, `WRITE_RANGE) write_fold (i_pc, i_woffs, w_addr);

    ram #(5, MAX_SIZE) opcode_ram (i_clk,
	    r_addr, opcode_out, w_addr, opcode_in, opcode_we);
    ram #(3, MAX_SIZE) modif_ram (i_clk,
	    r_addr, modif_out, w_addr, modif_in, modif_we);
    ram #(3, MAX_SIZE) amode_ram (i_clk,
            r_addr, amode_out, w_addr, amode_in, amode_we);
    ram #(`ADDR_WIDTH, MAX_SIZE) anumber_ram (i_clk,
            r_addr, anumber_out, w_addr, anumber_in, anumber_we);
    ram #(3, MAX_SIZE) bmode_ram (i_clk,
            r_addr, bmode_out, w_addr, bmode_in, bmode_we);
    ram #(`ADDR_WIDTH, MAX_SIZE) bnumber_ram (i_clk,
            r_addr, bnumber_out, w_addr, bnumber_in, bnumber_we);

endmodule

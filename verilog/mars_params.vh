`ifndef __mars_params_vh__
`define __masr_params_vh__

`define	CORESIZE	2000
`define ADDR_WIDTH	$clog2(`CORESIZE)
`define MAX_PROCESSES	`CORESIZE / 16

`define INSTR_WIDTH	14 + 2 * `ADDR_WIDTH

`define READ_RANGE	400
`define WRITE_RANGE	400

`endif

// vi:syntax=verilog

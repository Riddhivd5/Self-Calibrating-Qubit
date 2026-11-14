// ============================================================================
// discriminator_file_tb.v
//
// File-driven testbench for discriminator.v. Reads one line per clock cycle
// from the stimulus file (rst_n valid_in i_in q_in coef_a coef_b coef_c, all
// decimal), applies it before the rising edge, and after every rising edge
// writes "valid_out state_bit" to the response file. The response is compared
// with the cycle-accurate Python model by validate_discriminator.py.
//
//   iverilog -g2012 -o sim rtl/discriminator_file_tb.v rtl/discriminator.v
//   vvp sim +stim=stimulus.txt +resp=response.txt
// ============================================================================
`timescale 1ns / 1ps

module discriminator_file_tb;
    parameter DATA_WIDTH = 16;
    parameter FRAC_BITS  = 15;

    reg                         clk = 1'b0;
    reg                         rst_n = 1'b0;
    reg                         valid_in = 1'b0;
    reg signed [DATA_WIDTH-1:0] i_in = 0, q_in = 0, coef_a = 0, coef_b = 0, coef_c = 0;
    wire                        valid_out, state_bit;

    discriminator #(.DATA_WIDTH(DATA_WIDTH), .FRAC_BITS(FRAC_BITS)) dut (
        .clk(clk), .rst_n(rst_n), .valid_in(valid_in), .i_in(i_in), .q_in(q_in),
        .coef_a(coef_a), .coef_b(coef_b), .coef_c(coef_c), .valid_out(valid_out), .state_bit(state_bit));

    integer fin, fout, got, r, v, ii, qq, a, b, c;
    integer cycles;
    reg [1023:0] stim_name, resp_name;

    initial begin
        if (!$value$plusargs("stim=%s", stim_name)) stim_name = "stimulus.txt";
        if (!$value$plusargs("resp=%s", resp_name)) resp_name = "response.txt";
        fin  = $fopen(stim_name, "r");
        fout = $fopen(resp_name, "w");
        if (fin == 0 || fout == 0) begin $display("cannot open stimulus or response file"); $finish; end
        cycles = 0;
        got = $fscanf(fin, "%d %d %d %d %d %d %d\n", r, v, ii, qq, a, b, c);
        while (got == 7) begin
            rst_n = r[0]; valid_in = v[0]; i_in = ii; q_in = qq; coef_a = a; coef_b = b; coef_c = c;
            #5 clk = 1'b1;                      // rising edge: DUT samples the inputs applied above
            #1 $fwrite(fout, "%b %b\n", valid_out, state_bit);
            #4 clk = 1'b0;
            cycles = cycles + 1;
            got = $fscanf(fin, "%d %d %d %d %d %d %d\n", r, v, ii, qq, a, b, c);
        end
        $fclose(fin); $fclose(fout);
        $display("discriminator_file_tb: %0d cycles", cycles);
        $finish;
    end
endmodule

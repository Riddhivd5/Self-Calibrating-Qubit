// ============================================================================
// discriminator_tb.v
//
// Testbench for discriminator.v using real IQ points from q0, converted to
// Q1.15 via iq_fixedpoint.py (see iq_2026-09-11_08-58-08.npz, q0_state0 and
// q0_state1, first 3 shots of each).
//
// Boundary used here: a=1.0, b=0, c=0 — classify purely on the sign of I.
// This is a valid choice for q0 specifically because state 0 shots cluster
// at negative I and state 1 shots cluster at positive I in this dataset
// (checked against the real data before picking this boundary). This is
// NOT a general-purpose trained boundary — it's a minimal sanity check that
// the RTL classifies real points correctly on their obvious side of a line.
// ============================================================================

`timescale 1ns / 1ps

module discriminator_tb;

    parameter DATA_WIDTH = 16;
    parameter FRAC_BITS  = 15;
    parameter CLK_PERIOD = 10; // 100 MHz test clock — plenty of margin vs. 40ns budget

    reg                          clk;
    reg                          rst_n;
    reg                          valid_in;
    reg signed [DATA_WIDTH-1:0]  i_in, q_in;
    reg signed [DATA_WIDTH-1:0]  coef_a, coef_b, coef_c;

    wire                         valid_out;
    wire                         state_bit;

    integer errors;
    integer i;

    // Test vectors: {I, Q, expected_state}
    // Q1.15 values from real q0 data (see header comment)
    reg signed [DATA_WIDTH-1:0] test_i     [0:5];
    reg signed [DATA_WIDTH-1:0] test_q     [0:5];
    reg                         test_state [0:5];

    discriminator #(
        .DATA_WIDTH(DATA_WIDTH),
        .FRAC_BITS(FRAC_BITS)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .valid_in(valid_in),
        .i_in(i_in),
        .q_in(q_in),
        .coef_a(coef_a),
        .coef_b(coef_b),
        .coef_c(coef_c),
        .valid_out(valid_out),
        .state_bit(state_bit)
    );

    // Clock generation
    always #(CLK_PERIOD / 2) clk = ~clk;

    initial begin
        // q0_state0 samples -> expected state 0
        test_i[0] = -16'sd6629;  test_q[0] = -16'sd1853;  test_state[0] = 1'b0;
        test_i[1] = -16'sd11148; test_q[1] = -16'sd3332;  test_state[1] = 1'b0;
        test_i[2] = -16'sd9560;  test_q[2] = -16'sd1936;  test_state[2] = 1'b0;
        // q0_state1 samples -> expected state 1
        test_i[3] = 16'sd9642;   test_q[3] = -16'sd3487;  test_state[3] = 1'b1;
        test_i[4] = 16'sd10901;  test_q[4] = -16'sd3139;  test_state[4] = 1'b1;
        test_i[5] = 16'sd11719;  test_q[5] = 16'sd2413;   test_state[5] = 1'b1;
    end

    initial begin
        clk       = 1'b0;
        rst_n     = 1'b0;
        valid_in  = 1'b0;
        i_in      = 0;
        q_in      = 0;
        errors    = 0;

        // Boundary: classify on sign of I only (a=1.0, b=0, c=0 in Q1.15)
        coef_a = 16'sd32767; // ~1.0 in Q1.15
        coef_b = 16'sd0;
        coef_c = 16'sd0;

        repeat (2) @(posedge clk);
        rst_n = 1'b1;
        repeat (2) @(posedge clk);

        for (i = 0; i < 6; i = i + 1) begin
            @(posedge clk);
            #1; // avoid a race with the DUT's own posedge-triggered sampling
            i_in     = test_i[i];
            q_in     = test_q[i];
            valid_in = 1'b1;
            @(posedge clk);
            #1;
            valid_in = 1'b0;

            // Wait for the 3-cycle pipeline latency
            repeat (3) @(posedge clk);

            if (valid_out !== 1'b1) begin
                $display("FAIL: vector %0d — valid_out not asserted", i);
                errors = errors + 1;
            end else if (state_bit !== test_state[i]) begin
                $display("FAIL: vector %0d — I=%0d Q=%0d expected=%0d got=%0d",
                          i, test_i[i], test_q[i], test_state[i], state_bit);
                errors = errors + 1;
            end else begin
                $display("PASS: vector %0d — I=%0d Q=%0d -> state=%0d",
                          i, test_i[i], test_q[i], state_bit);
            end
        end

        if (errors == 0)
            $display("\nALL TESTS PASSED");
        else
            $display("\n%0d TEST(S) FAILED", errors);

        $finish;
    end

endmodule

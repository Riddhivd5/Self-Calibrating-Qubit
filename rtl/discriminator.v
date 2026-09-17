// ============================================================================
// discriminator.v
//
// Baseline readout discriminator. Classifies an (I, Q) point as state 0 or
// state 1 based on a linear decision boundary:
//
//     a*I + b*Q + c > 0   ->  state = 1
//     a*I + b*Q + c <= 0  ->  state = 0
//
// (a, b, c) are the boundary coefficients — think of them as defining a
// straight line on the IQ plane. This is intentionally the simplest possible
// classifier; it gets replaced/adapted later in the project once a real
// trained boundary and drift-adaptation logic are added.
//
// Data format: all I/O and coefficients are Q1.15 signed fixed-point
// (1 sign bit, 15 fractional bits, 16 bits total) — see iq_fixedpoint.py
// for the matching software reference.
//
// 3-stage pipeline (register inputs -> multiply -> add & compare) so this
// comfortably meets timing at typical FPGA clock speeds. Note: 3 clock
// cycles of *latency* is not the same as the ~40ns *throughput* budget the
// project targets — pipelining is exactly what lets a new decision start
// every clock cycle even though each individual decision takes 3 cycles to
// come out the other end.
// ============================================================================

module discriminator #(
    parameter DATA_WIDTH = 16,   // Q1.15: 16 bits total
    parameter FRAC_BITS  = 15    // 15 fractional bits
)(
    input  wire                        clk,
    input  wire                        rst_n,      // active-low synchronous reset

    input  wire                        valid_in,
    input  wire signed [DATA_WIDTH-1:0] i_in,       // Q1.15
    input  wire signed [DATA_WIDTH-1:0] q_in,       // Q1.15

    input  wire signed [DATA_WIDTH-1:0] coef_a,     // Q1.15 — weight on I
    input  wire signed [DATA_WIDTH-1:0] coef_b,     // Q1.15 — weight on Q
    input  wire signed [DATA_WIDTH-1:0] coef_c,     // Q1.15 — offset/threshold

    output reg                         valid_out,
    output reg                         state_bit    // 0 or 1 classification
);

    // ---- Stage 1: register inputs ----
    reg signed [DATA_WIDTH-1:0] i_s1, q_s1;
    reg signed [DATA_WIDTH-1:0] coef_a_s1, coef_b_s1, coef_c_s1;
    reg                         valid_s1;

    always @(posedge clk) begin
        if (!rst_n) begin
            i_s1      <= {DATA_WIDTH{1'b0}};
            q_s1      <= {DATA_WIDTH{1'b0}};
            coef_a_s1 <= {DATA_WIDTH{1'b0}};
            coef_b_s1 <= {DATA_WIDTH{1'b0}};
            coef_c_s1 <= {DATA_WIDTH{1'b0}};
            valid_s1  <= 1'b0;
        end else begin
            i_s1      <= i_in;
            q_s1      <= q_in;
            coef_a_s1 <= coef_a;
            coef_b_s1 <= coef_b;
            coef_c_s1 <= coef_c;
            valid_s1  <= valid_in;
        end
    end

    // ---- Stage 2: multiply (maps onto DSP slices) ----
    // Q1.15 * Q1.15 -> Q2.30 (32-bit signed product)
    localparam PROD_WIDTH = 2 * DATA_WIDTH;

    reg signed [PROD_WIDTH-1:0] prod_a_s2, prod_b_s2;
    reg signed [DATA_WIDTH-1:0] coef_c_s2;
    reg                         valid_s2;

    always @(posedge clk) begin
        if (!rst_n) begin
            prod_a_s2 <= {PROD_WIDTH{1'b0}};
            prod_b_s2 <= {PROD_WIDTH{1'b0}};
            coef_c_s2 <= {DATA_WIDTH{1'b0}};
            valid_s2  <= 1'b0;
        end else begin
            prod_a_s2 <= i_s1 * coef_a_s1;
            prod_b_s2 <= q_s1 * coef_b_s1;
            coef_c_s2 <= coef_c_s1;
            valid_s2  <= valid_s1;
        end
    end

    // ---- Stage 3: sum + compare ----
    // Align coef_c (Q1.15) to the product format (Q2.30) by shifting left
    // by FRAC_BITS before adding, so all three terms share the same
    // fractional scale before the comparison.
    localparam SUM_WIDTH = PROD_WIDTH + 2; // headroom to avoid overflow on the add

    wire signed [SUM_WIDTH-1:0] sum_comb =
        $signed({{2{prod_a_s2[PROD_WIDTH-1]}}, prod_a_s2}) +
        $signed({{2{prod_b_s2[PROD_WIDTH-1]}}, prod_b_s2}) +
        ($signed(coef_c_s2) <<< FRAC_BITS);

    always @(posedge clk) begin
        if (!rst_n) begin
            state_bit <= 1'b0;
            valid_out <= 1'b0;
        end else begin
            state_bit <= ~sum_comb[SUM_WIDTH-1]; // sum >= 0 -> state 1
            valid_out <= valid_s2;
        end
    end

endmodule

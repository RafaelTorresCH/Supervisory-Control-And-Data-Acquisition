module tone_bank_4 (
    input  wire               clk_48k,
    input  wire               rst_n,
    input  wire               btn_n0,
    input  wire               btn_n1,
    input  wire               btn_n2,
    input  wire               btn_n3,
    output wire signed [15:0] audio_out
);

    reg [31:0] phase0, phase1, phase2, phase3;

    localparam [31:0] STEP_C4 = 32'd233736598; // ~261.63 Hz @ 48 kHz
    localparam [31:0] STEP_E4 = 32'd294441963; // ~329.63 Hz @ 48 kHz
    localparam [31:0] STEP_G4 = 32'd350254042; // ~392.00 Hz @ 48 kHz
    localparam [31:0] STEP_A4 = 32'd393705335; // ~440.00 Hz @ 48 kHz

    wire signed [15:0] s0, s1, s2, s3;
    wire signed [17:0] mix_sum;

    always @(posedge clk_48k or negedge rst_n) begin
        if (!rst_n) begin
            phase0 <= 32'd0;
            phase1 <= 32'd0;
            phase2 <= 32'd0;
            phase3 <= 32'd0;
        end else begin
            if (!btn_n0) phase0 <= phase0 + STEP_C4;
            if (!btn_n1) phase1 <= phase1 + STEP_E4;
            if (!btn_n2) phase2 <= phase2 + STEP_G4;
            if (!btn_n3) phase3 <= phase3 + STEP_A4;
        end
    end

    assign s0 = (!btn_n0) ? (phase0[31] ? 16'sd3000 : -16'sd3000) : 16'sd0;
    assign s1 = (!btn_n1) ? (phase1[31] ? 16'sd3000 : -16'sd3000) : 16'sd0;
    assign s2 = (!btn_n2) ? (phase2[31] ? 16'sd3000 : -16'sd3000) : 16'sd0;
    assign s3 = (!btn_n3) ? (phase3[31] ? 16'sd3000 : -16'sd3000) : 16'sd0;

    assign mix_sum  = s0 + s1 + s2 + s3;
    assign audio_out = mix_sum >>> 2;

endmodule
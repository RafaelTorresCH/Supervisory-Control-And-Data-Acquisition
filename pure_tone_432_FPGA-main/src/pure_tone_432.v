module pure_tone_432 (
    input  wire             clk_48k,
    input  wire             rst_n,
    input  wire [15:0]      phase_inc,
    output reg signed [15:0] audio_out
);

    reg [15:0] phase_acc;
    reg signed [15:0] sine_lut [0:31];
    wire [4:0] lut_index;

    assign lut_index = phase_acc[15:11];

    initial begin
        sine_lut[0]  = 16'sd0;
        sine_lut[1]  = 16'sd6393;
        sine_lut[2]  = 16'sd12539;
        sine_lut[3]  = 16'sd18204;
        sine_lut[4]  = 16'sd23170;
        sine_lut[5]  = 16'sd27245;
        sine_lut[6]  = 16'sd30273;
        sine_lut[7]  = 16'sd32137;
        sine_lut[8]  = 16'sd32767;
        sine_lut[9]  = 16'sd32137;
        sine_lut[10] = 16'sd30273;
        sine_lut[11] = 16'sd27245;
        sine_lut[12] = 16'sd23170;
        sine_lut[13] = 16'sd18204;
        sine_lut[14] = 16'sd12539;
        sine_lut[15] = 16'sd6393;
        sine_lut[16] = 16'sd0;
        sine_lut[17] = -16'sd6393;
        sine_lut[18] = -16'sd12539;
        sine_lut[19] = -16'sd18204;
        sine_lut[20] = -16'sd23170;
        sine_lut[21] = -16'sd27245;
        sine_lut[22] = -16'sd30273;
        sine_lut[23] = -16'sd32137;
        sine_lut[24] = -16'sd32767;
        sine_lut[25] = -16'sd32137;
        sine_lut[26] = -16'sd30273;
        sine_lut[27] = -16'sd27245;
        sine_lut[28] = -16'sd23170;
        sine_lut[29] = -16'sd18204;
        sine_lut[30] = -16'sd12539;
        sine_lut[31] = -16'sd6393;
    end

    always @(posedge clk_48k or negedge rst_n) begin
        if (!rst_n) begin
            phase_acc <= 16'd0;
            audio_out <= 16'sd0;
        end else begin
            phase_acc <= phase_acc + phase_inc;
            audio_out <= sine_lut[lut_index];
        end
    end

endmodule
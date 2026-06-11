module top_audio (
    input  wire clk_27m,
    input  wire btn_n0,
    input  wire btn_n1,
    input  wire btn_n2,
    input  wire btn_n3,
    output wire i2s_bclk,
    output wire i2s_lrclk,
    output wire i2s_dacdat,
    output wire pa_en
);

    wire clk_12m;
    wire lrclk_wire;
    wire signed [15:0] audio_signal;

    assign pa_en = 1'b1;
    assign i2s_lrclk = lrclk_wire;

    Gowin_rPLL pll_inst (
        .clkout(clk_12m),
        .clkin(clk_27m)
    );

    tone_bank_4 tone_inst (
        .clk_48k(lrclk_wire),
        .rst_n(1'b1),
        .btn_n0(btn_n0),
        .btn_n1(btn_n1),
        .btn_n2(btn_n2),
        .btn_n3(btn_n3),
        .audio_out(audio_signal)
    );

    i2s_tx tx_module (
        .clk_12m(clk_12m),
        .rst_n(1'b1),
        .audio_l(audio_signal),
        .audio_r(audio_signal),
        .i2s_bclk(i2s_bclk),
        .i2s_lrclk(lrclk_wire),
        .i2s_dacdat(i2s_dacdat)
    );

endmodule
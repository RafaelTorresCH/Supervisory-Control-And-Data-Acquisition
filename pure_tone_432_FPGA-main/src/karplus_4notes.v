module karplus_4notes (
    input  wire              clk_48k,
    input  wire              rst_n,
    input  wire              btn_n0,
    input  wire              btn_n1,
    input  wire              btn_n2,
    input  wire              btn_n3,
    output reg signed [15:0] audio_out
);

    parameter MAX_LEN = 256;

    reg signed [15:0] buffer [0:MAX_LEN-1];
    reg [7:0] wr_ptr;
    reg [7:0] delay_len;

    reg btn0_d, btn1_d, btn2_d, btn3_d;
    wire trig0, trig1, trig2, trig3;

    reg [7:0] init_i;
    reg init_active;

    reg [15:0] lfsr;
    wire fb_bit;

    reg [7:0] rd_ptr1, rd_ptr2;
    reg signed [15:0] s1, s2;
    reg signed [16:0] avg;
    reg signed [31:0] fb_mult;
    reg signed [15:0] new_sample;

    integer k;

    assign trig0 = (btn0_d == 1'b1) && (btn_n0 == 1'b0);
    assign trig1 = (btn1_d == 1'b1) && (btn_n1 == 1'b0);
    assign trig2 = (btn2_d == 1'b1) && (btn_n2 == 1'b0);
    assign trig3 = (btn3_d == 1'b1) && (btn_n3 == 1'b0);

    assign fb_bit = lfsr[15] ^ lfsr[13] ^ lfsr[12] ^ lfsr[10];

    initial begin
        for (k = 0; k < MAX_LEN; k = k + 1)
            buffer[k] = 16'sd0;

        wr_ptr      = 8'd0;
        delay_len   = 8'd183;
        btn0_d      = 1'b1;
        btn1_d      = 1'b1;
        btn2_d      = 1'b1;
        btn3_d      = 1'b1;
        init_i      = 8'd0;
        init_active = 1'b0;
        lfsr        = 16'hACE1;
        audio_out   = 16'sd0;
    end

    always @(posedge clk_48k or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr      <= 8'd0;
            delay_len   <= 8'd183;
            btn0_d      <= 1'b1;
            btn1_d      <= 1'b1;
            btn2_d      <= 1'b1;
            btn3_d      <= 1'b1;
            init_i      <= 8'd0;
            init_active <= 1'b0;
            lfsr        <= 16'hACE1;
            audio_out   <= 16'sd0;

            for (k = 0; k < MAX_LEN; k = k + 1)
                buffer[k] <= 16'sd0;
        end else begin
            btn0_d <= btn_n0;
            btn1_d <= btn_n1;
            btn2_d <= btn_n2;
            btn3_d <= btn_n3;

            if (trig0) begin
                delay_len   <= 8'd183; // Do4 aprox
                wr_ptr      <= 8'd0;
                init_i      <= 8'd0;
                init_active <= 1'b1;
            end else if (trig1) begin
                delay_len   <= 8'd163; // Re4 aprox
                wr_ptr      <= 8'd0;
                init_i      <= 8'd0;
                init_active <= 1'b1;
            end else if (trig2) begin
                delay_len   <= 8'd152; // Mi4 aprox
                wr_ptr      <= 8'd0;
                init_i      <= 8'd0;
                init_active <= 1'b1;
            end else if (trig3) begin
                delay_len   <= 8'd143; // Fa4 aprox
                wr_ptr      <= 8'd0;
                init_i      <= 8'd0;
                init_active <= 1'b1;
            end

            if (init_active) begin
                lfsr <= {lfsr[14:0], fb_bit};

                if (init_i < delay_len) begin
                    buffer[init_i] <= lfsr[15] ? 16'sd6000 : -16'sd6000;
                    init_i <= init_i + 8'd1;
                    audio_out <= 16'sd0;
                end else begin
                    init_active <= 1'b0;
                    wr_ptr <= 8'd0;
                end
            end else begin
                rd_ptr1 = wr_ptr;

                if (wr_ptr == delay_len - 1)
                    rd_ptr2 = 8'd0;
                else
                    rd_ptr2 = wr_ptr + 8'd1;

                s1 = buffer[rd_ptr1];
                s2 = buffer[rd_ptr2];

                avg = (s1 + s2) >>> 1;

                // feedback un poco menor para suavizar el decay
                fb_mult = avg * 16'sd32000;
                new_sample = fb_mult >>> 15;

                buffer[wr_ptr] <= new_sample;
                audio_out <= new_sample;

                if (wr_ptr == delay_len - 1)
                    wr_ptr <= 8'd0;
                else
                    wr_ptr <= wr_ptr + 8'd1;
            end
        end
    end

endmodule
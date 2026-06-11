module string_voice #(
    parameter MAX_LEN    = 256,
    parameter DELAY_LEN  = 183,
    parameter EXCITE_AMP = 16'sd5000,
    parameter FEEDBACK   = 16'sd32100
)(
    input  wire              clk_48k,
    input  wire              rst_n,
    input  wire              trig,
    output reg signed [15:0] audio_out
);

    reg trig_d;
    reg init_active;
    reg [7:0] init_i;
    reg [7:0] wr_ptr;

    reg [15:0] lfsr;
    wire fb_bit;

    reg signed [15:0] buffer [0:MAX_LEN-1];
    reg signed [15:0] s1, s2;
    reg signed [16:0] avg;
    reg signed [31:0] mult_fb;
    reg signed [15:0] next_sample;
    reg signed [15:0] clipped;

    integer k;

    assign fb_bit = lfsr[15] ^ lfsr[13] ^ lfsr[12] ^ lfsr[10];

    function signed [15:0] soft_clip;
        input signed [15:0] x;
        begin
            if (x > 16'sd12000)
                soft_clip = 16'sd12000 + ((x - 16'sd12000) >>> 2);
            else if (x < -16'sd12000)
                soft_clip = -16'sd12000 + ((x + 16'sd12000) >>> 2);
            else
                soft_clip = x;
        end
    endfunction

    initial begin
        for (k = 0; k < MAX_LEN; k = k + 1)
            buffer[k] = 16'sd0;

        trig_d      = 1'b0;
        init_active = 1'b0;
        init_i      = 8'd0;
        wr_ptr      = 8'd0;
        lfsr        = 16'hACE1;
        audio_out   = 16'sd0;
    end

    always @(posedge clk_48k or negedge rst_n) begin
        if (!rst_n) begin
            trig_d      <= 1'b0;
            init_active <= 1'b0;
            init_i      <= 8'd0;
            wr_ptr      <= 8'd0;
            lfsr        <= 16'hACE1;
            audio_out   <= 16'sd0;

            for (k = 0; k < MAX_LEN; k = k + 1)
                buffer[k] <= 16'sd0;
        end else begin
            trig_d <= trig;

            if (trig && !trig_d) begin
                init_active <= 1'b1;
                init_i      <= 8'd0;
                wr_ptr      <= 8'd0;
            end

            if (init_active) begin
                lfsr <= {lfsr[14:0], fb_bit};

                if (init_i < DELAY_LEN) begin
                    buffer[init_i] <= lfsr[0] ? EXCITE_AMP : -EXCITE_AMP;
                    init_i <= init_i + 8'd1;
                    audio_out <= 16'sd0;
                end else begin
                    init_active <= 1'b0;
                    wr_ptr <= 8'd0;
                end
            end else begin
                s1 = buffer[wr_ptr];

                if (wr_ptr == DELAY_LEN - 1)
                    s2 = buffer[0];
                else
                    s2 = buffer[wr_ptr + 1];

                avg = (s1 + s2) >>> 1;
                mult_fb = avg * FEEDBACK;
                next_sample = mult_fb >>> 15;
                clipped = soft_clip(next_sample);

                buffer[wr_ptr] <= clipped;
                audio_out <= clipped;

                if (wr_ptr == DELAY_LEN - 1)
                    wr_ptr <= 8'd0;
                else
                    wr_ptr <= wr_ptr + 8'd1;
            end
        end
    end

endmodule
module pluck_env (
    input  wire        clk_48k,
    input  wire        rst_n,
    input  wire        trigger,
    output reg [15:0]  env
);

    reg trigger_d;

    always @(posedge clk_48k or negedge rst_n) begin
        if (!rst_n) begin
            env       <= 16'd0;
            trigger_d <= 1'b0;
        end else begin
            trigger_d <= trigger;

            // flanco de subida del trigger
            if (trigger && !trigger_d) begin
                env <= 16'd32767;
            end else if (env > 16'd180) begin
                env <= env - 16'd180;
            end else begin
                env <= 16'd0;
            end
        end
    end

endmodule
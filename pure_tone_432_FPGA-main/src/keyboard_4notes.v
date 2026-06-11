module keyboard_4notes (
    input  wire btn_n0,
    input  wire btn_n1,
    input  wire btn_n2,
    input  wire btn_n3,
    output reg        note_on,
    output reg [15:0] phase_inc
);

    always @(*) begin
        note_on   = 1'b0;
        phase_inc = 16'd0;

        if (btn_n0 == 1'b0) begin
            note_on   = 1'b1;
            phase_inc = 16'd358; // Do
        end
        else if (btn_n1 == 1'b0) begin
            note_on   = 1'b1;
            phase_inc = 16'd402; // Re
        end
        else if (btn_n2 == 1'b0) begin
            note_on   = 1'b1;
            phase_inc = 16'd451; // Mi
        end
        else if (btn_n3 == 1'b0) begin
            note_on   = 1'b1;
            phase_inc = 16'd478; // Fa
        end
    end

endmodule
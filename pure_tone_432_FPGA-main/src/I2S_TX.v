// ==========================================
// Módulo 3: Transmisor I2S (16-bit, 48kHz)
// Archivo: I2S_TX.v
// ==========================================
module i2s_tx (
    input  wire clk_12m,       // Reloj limpio de 12.288 MHz (Desde el PLL)
    input  wire rst_n,         // Reset activo en bajo
    input  wire signed [15:0] audio_l, // Audio Canal Izquierdo (Desde tu Módulo 2)
    input  wire signed [15:0] audio_r, // Audio Canal Derecho  (Desde tu Módulo 2)
    
    // Pines físicos hacia el Codec de audio
    output wire i2s_bclk,      // Reloj de bit (1.536 MHz)
    output wire i2s_lrclk,     // Reloj de canal (Left/Right a 48 kHz)
    output reg  i2s_dacdat     // Datos seriales
);

    // Divisores de reloj
    reg [2:0] bclk_div;        // Divide 12.288MHz por 8 = 1.536 MHz
    reg [4:0] lrclk_div;       // Cuenta 32 bits (16 izq + 16 der)
    
    // Registros de desplazamiento (Shift Registers)
    reg [15:0] shift_l;
    reg [15:0] shift_r;

    // Generación de BCLK (Invirtiendo el bit más alto del divisor)
    assign i2s_bclk = bclk_div[2]; 
    
    // Generación de LRCLK (0 = Izquierdo, 1 = Derecho)
    assign i2s_lrclk = lrclk_div[4];

    // Bucle principal a 12.288 MHz
    always @(posedge clk_12m or negedge rst_n) begin
        if (!rst_n) begin
            bclk_div   <= 3'd0;
            lrclk_div  <= 5'd0;
            shift_l    <= 16'd0;
            shift_r    <= 16'd0;
            i2s_dacdat <= 1'b0;
        end else begin
            // El BCLK cambia cada 4 ciclos de clk_12m
            bclk_div <= bclk_div + 1'b1;

            // En el flanco de BAJADA del BCLK (cuando bclk_div pasa de 3 a 4)
            // preparamos el siguiente bit de datos. El estándar I2S dice que 
            // los datos cambian en la bajada para ser leídos en la subida.
            if (bclk_div == 3'd7) begin
                lrclk_div <= lrclk_div + 1'b1;

                // El protocolo I2S tiene un retraso de 1 ciclo de reloj.
                // Cargamos los datos nuevos justo cuando LRCLK cambia.
                if (lrclk_div == 5'd0) begin
                    // Empieza canal izquierdo (Cargamos L, preparamos R)
                    shift_l <= audio_l;
                    shift_r <= audio_r;
                end

                // Sacar el bit correspondiente al cable serial
                if (lrclk_div < 5'd16) begin
                    // Transmitiendo Canal Izquierdo (MSB primero)
                    i2s_dacdat <= shift_l[15 - lrclk_div[3:0]];
                end else begin
                    // Transmitiendo Canal Derecho (MSB primero)
                    i2s_dacdat <= shift_r[15 - lrclk_div[3:0]];
                end
            end
        end
    end

endmodule
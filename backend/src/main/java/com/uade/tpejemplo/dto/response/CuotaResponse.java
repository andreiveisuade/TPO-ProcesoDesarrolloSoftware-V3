package com.uade.tpejemplo.dto.response;

import com.uade.tpejemplo.model.interfaces.ICuota;
import lombok.AllArgsConstructor;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;

@Data
@AllArgsConstructor
public class CuotaResponse {

    private Long idCredito;
    private Integer numeroCuota;
    private BigDecimal importe;
    private LocalDate fechaVencimiento;
    private boolean pagada;

    public static CuotaResponse desde(ICuota cuota) {
        return new CuotaResponse(
            cuota.getCredito().getId(),
            cuota.getNumero(),
            cuota.getImporte(),
            cuota.getFechaVencimiento(),
            cuota.estaPagada()
        );
    }
}

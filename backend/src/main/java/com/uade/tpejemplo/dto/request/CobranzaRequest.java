package com.uade.tpejemplo.dto.request;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Data;

import java.math.BigDecimal;

@Data
public class CobranzaRequest {

    @NotNull(message = "El ID del crédito es obligatorio")
    private Long idCredito;

    @NotNull(message = "El número de cuota es obligatorio")
    private Integer numeroCuota;

    @NotNull(message = "El importe es obligatorio")
    @Positive(message = "El importe debe ser mayor a cero")
    private BigDecimal importe;
}

package com.uade.tpejemplo.dto.request;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;

@Data
public class CreditoRequest {

    @NotBlank(message = "El DNI del cliente es obligatorio")
    private String dniCliente;

    @NotNull(message = "La deuda original es obligatoria")
    @Positive(message = "La deuda original debe ser mayor a cero")
    private BigDecimal deudaOriginal;

    @NotNull(message = "La fecha es obligatoria")
    private LocalDate fecha;

    /** Porcentaje unico sobre el capital: 45 significa 45 %. */
    @NotNull(message = "La tasa de interes es obligatoria")
    @DecimalMin(value = "0", message = "La tasa de interes no puede ser negativa")
    @DecimalMax(value = "999.99", message = "La tasa de interes es demasiado alta")
    private BigDecimal tasaInteres;

    @NotNull(message = "La cantidad de cuotas es obligatoria")
    @Min(value = 1, message = "Debe tener al menos 1 cuota")
    private Integer cantidadCuotas;
}

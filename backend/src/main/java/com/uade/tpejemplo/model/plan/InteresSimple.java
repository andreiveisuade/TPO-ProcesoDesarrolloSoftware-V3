package com.uade.tpejemplo.model.plan;

import com.uade.tpejemplo.model.interfaces.CalculoDeCuota;

import java.math.BigDecimal;
import java.math.RoundingMode;

// La tasa es un porcentaje unico sobre el total prestado: un credito de
// 10.000 al 45% se devuelve siempre por 14.500, sea en 6 cuotas o en 24.
// Strategy: estrategia concreta
public class InteresSimple implements CalculoDeCuota {

    private static final BigDecimal CIEN = new BigDecimal("100");

    private BigDecimal totalADevolver(BigDecimal capital, BigDecimal tasaInteres) {
        BigDecimal coeficiente = BigDecimal.ONE.add(tasaInteres.divide(CIEN, 4, RoundingMode.HALF_UP));
        return capital.multiply(coeficiente).setScale(2, RoundingMode.HALF_UP);
    }

    @Override
    public BigDecimal importeCuota(BigDecimal capital, BigDecimal tasaInteres, int cantidadCuotas) {
        return totalADevolver(capital, tasaInteres)
            .divide(BigDecimal.valueOf(cantidadCuotas), 2, RoundingMode.HALF_UP);
    }
}

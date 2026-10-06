package com.uade.tpejemplo.model.plan;

import com.uade.tpejemplo.model.interfaces.CalculoDeCuota;

import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;

/**
 * La tasa es mensual sobre el saldo: cuota fija = C * i / (1 - (1 + i)^-n).
 * Con tasa 0 la cuota es el capital dividido en partes iguales.
 */
public class SistemaFrances implements CalculoDeCuota {

    private static final MathContext PRECISION = MathContext.DECIMAL64;

    @Override
    public BigDecimal importeCuota(BigDecimal capital, BigDecimal tasaInteres, int cantidadCuotas) {
        BigDecimal i = tasaInteres.divide(new BigDecimal("100"), PRECISION);
        if (i.signum() == 0) {
            return capital.divide(BigDecimal.valueOf(cantidadCuotas), 2, RoundingMode.HALF_UP);
        }
        BigDecimal descuento = BigDecimal.ONE.subtract(
            BigDecimal.ONE.divide(BigDecimal.ONE.add(i).pow(cantidadCuotas, PRECISION), PRECISION));
        return capital.multiply(i).divide(descuento, 2, RoundingMode.HALF_UP);
    }

    @Override
    public BigDecimal totalADevolver(BigDecimal capital, BigDecimal tasaInteres, int cantidadCuotas) {
        return importeCuota(capital, tasaInteres, cantidadCuotas).multiply(BigDecimal.valueOf(cantidadCuotas));
    }
}

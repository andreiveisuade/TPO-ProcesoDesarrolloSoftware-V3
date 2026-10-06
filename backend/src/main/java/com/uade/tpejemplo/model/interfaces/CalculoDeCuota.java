package com.uade.tpejemplo.model.interfaces;

import java.math.BigDecimal;

// Strategy: interfaz comun del calculo de cuota
public interface CalculoDeCuota {

    BigDecimal importeCuota(BigDecimal capital, BigDecimal tasaInteres, int cantidadCuotas);
}

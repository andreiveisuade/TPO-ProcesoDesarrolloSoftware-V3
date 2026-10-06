package com.uade.tpejemplo.model.interfaces;

import java.math.BigDecimal;

public interface CalculoDeCuota {

    BigDecimal importeCuota(BigDecimal capital, BigDecimal tasaInteres, int cantidadCuotas);
}

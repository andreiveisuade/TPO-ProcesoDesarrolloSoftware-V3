package com.uade.tpejemplo.model.interfaces;

import java.math.BigDecimal;
import java.time.LocalDate;

public interface ICuota {

    Long getId();

    ICredito getCredito();

    Integer getNumero();

    BigDecimal getImporte();

    LocalDate getFechaVencimiento();

    boolean estaPagada();

    ICobranza registrarCobranza(BigDecimal importe);
}

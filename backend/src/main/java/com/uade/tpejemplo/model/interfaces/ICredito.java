package com.uade.tpejemplo.model.interfaces;

import com.uade.tpejemplo.model.EstadoCredito;
import com.uade.tpejemplo.model.TipoPlan;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

public interface ICredito {

    Long getId();

    ICliente getCliente();

    BigDecimal getDeudaOriginal();

    LocalDate getFecha();

    BigDecimal getTasaInteres();

    TipoPlan getTipoPlan();

    BigDecimal getImporteCuota();

    Integer getCantidadCuotas();

    boolean isAnulado();

    BigDecimal totalADevolver();

    List<? extends ICuota> getCuotas();

    EstadoCredito estado();

    BigDecimal saldo();

    boolean estaCancelado();

    boolean tieneCobranzas();

    boolean puedeAnularse();

    void anular();
}

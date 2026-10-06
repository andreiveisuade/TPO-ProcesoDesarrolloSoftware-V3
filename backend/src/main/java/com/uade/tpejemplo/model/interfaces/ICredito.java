package com.uade.tpejemplo.model.interfaces;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

public interface ICredito {

    Long getId();

    ICliente getCliente();

    BigDecimal getDeudaOriginal();

    LocalDate getFecha();

    BigDecimal getTasaInteres();

    BigDecimal getImporteCuota();

    Integer getCantidadCuotas();

    boolean isAnulado();

    BigDecimal totalADevolver();

    List<? extends ICuota> generarPlanDeCuotas();

    void anular(boolean tieneCobranzas);
}

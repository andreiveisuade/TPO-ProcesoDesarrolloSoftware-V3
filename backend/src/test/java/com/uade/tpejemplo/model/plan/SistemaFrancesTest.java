package com.uade.tpejemplo.model.plan;

import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.assertj.core.api.Assertions.assertThat;

class SistemaFrancesTest {

    private final SistemaFrances calculo = new SistemaFrances();

    @Test
    void cuotaFijaSegunLaFormulaFrancesa() {
        // 1000 x 0.10 / (1 - 1.1^-2) = 576.190...
        assertThat(calculo.importeCuota(new BigDecimal("1000"), new BigDecimal("10"), 2))
            .isEqualByComparingTo("576.19");
    }

    @Test
    void totalEsLaSumaExactaDeLasCuotas() {
        BigDecimal cuota = calculo.importeCuota(new BigDecimal("1000"), new BigDecimal("10"), 2);

        assertThat(calculo.totalADevolver(new BigDecimal("1000"), new BigDecimal("10"), 2))
            .isEqualByComparingTo("1152.38")
            .isEqualByComparingTo(cuota.multiply(BigDecimal.valueOf(2)));
    }

    @Test
    void tasaCeroDivideElCapitalEnPartesIguales() {
        assertThat(calculo.importeCuota(new BigDecimal("1000"), BigDecimal.ZERO, 4))
            .isEqualByComparingTo("250.00");
    }

    @Test
    void tasaCeroConRedondeoPierdeUnCentavoContraElCapital() {
        assertThat(calculo.importeCuota(new BigDecimal("1000"), BigDecimal.ZERO, 3)).isEqualByComparingTo("333.33");
        assertThat(calculo.totalADevolver(new BigDecimal("1000"), BigDecimal.ZERO, 3)).isEqualByComparingTo("999.99");
    }
}

package com.uade.tpejemplo.model.plan;

import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.assertj.core.api.Assertions.assertThat;

class InteresSimpleTest {

    private final InteresSimple calculo = new InteresSimple();

    @Test
    void cuotaRepartePorIgualCapitalMasLaTasa() {
        assertThat(calculo.importeCuota(new BigDecimal("10000"), new BigDecimal("45"), 24))
            .isEqualByComparingTo("604.17");
    }

    @Test
    void cuotaRedondeaAlCentavoYLaSumaSePasaDosCentavos() {
        BigDecimal cuota = calculo.importeCuota(new BigDecimal("10000"), new BigDecimal("45"), 6);

        assertThat(cuota).isEqualByComparingTo("2416.67");
        // 6 x 2416.67 = 14500.02: las cuotas cobran 2 centavos mas que capital + tasa
        assertThat(cuota.multiply(BigDecimal.valueOf(6))).isEqualByComparingTo("14500.02");
    }

    @Test
    void tasaCeroDevuelveElCapitalYLaSumaQuedaUnCentavoAbajo() {
        BigDecimal capital = new BigDecimal("1000");

        BigDecimal cuota = calculo.importeCuota(capital, BigDecimal.ZERO, 3);
        assertThat(cuota).isEqualByComparingTo("333.33");
        assertThat(cuota.multiply(BigDecimal.valueOf(3))).isEqualByComparingTo("999.99");
    }

    @Test
    void tasaConDecimalesRedondeaElCoeficienteACuatroDecimales() {
        // 12.345% -> 0.12345 -> 0.1235 -> 1000 x 1.1235
        assertThat(calculo.importeCuota(new BigDecimal("1000"), new BigDecimal("12.345"), 1))
            .isEqualByComparingTo("1123.50");
    }
}

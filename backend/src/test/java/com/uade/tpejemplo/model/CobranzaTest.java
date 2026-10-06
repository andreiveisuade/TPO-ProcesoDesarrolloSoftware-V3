package com.uade.tpejemplo.model;

import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.LocalDate;

import static org.assertj.core.api.Assertions.assertThat;

class CobranzaTest {

    @Test
    void seRegistraConFechaDeHoyYSePuedeAnularElMismoDia() {
        Credito credito = Credito.nuevo(Cliente.nuevo("30111222", "Ana"), new BigDecimal("100"),
            LocalDate.now(), BigDecimal.ZERO, 1, TipoPlan.INTERES_SIMPLE);
        Cobranza cobranza = credito.generarPlanDeCuotas().get(0).registrarCobranza(new BigDecimal("100.00"));

        assertThat(cobranza.getFechaCobranza()).isEqualTo(LocalDate.now());
        cobranza.anular();
        assertThat(cobranza.isAnulada()).isTrue();
    }

    // Sin cubrir: el rechazo de anular una cobranza de otro dia. La fecha la fija
    // el constructor con LocalDate.now() y no hay setter ni Clock inyectable.
}

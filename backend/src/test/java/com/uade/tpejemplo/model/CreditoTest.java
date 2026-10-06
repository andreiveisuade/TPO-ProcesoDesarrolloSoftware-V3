package com.uade.tpejemplo.model;

import com.uade.tpejemplo.exception.BusinessException;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.LocalDate;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class CreditoTest {

    private Credito creditoDeTresCuotas() {
        Credito credito = Credito.nuevo(Cliente.nuevo("30111222", "Ana"), new BigDecimal("900"),
            LocalDate.now(), BigDecimal.ZERO, 3, TipoPlan.INTERES_SIMPLE);
        credito.generarPlanDeCuotas();
        return credito;
    }

    private void pagar(Cuota cuota) {
        cuota.registrarCobranza(cuota.getImporte());
    }

    @Test
    void generaUnaCuotaPorMesDesdeLaFecha() {
        Credito credito = creditoDeTresCuotas();

        assertThat(credito.getCuotas()).hasSize(3);
        assertThat(credito.getCuotas().get(0).getFechaVencimiento()).isEqualTo(LocalDate.now().plusMonths(1));
        assertThat(credito.getImporteCuota()).isEqualByComparingTo("300.00");
    }

    @Test
    void nuevoEstaVigenteConSaldoIgualAlTotal() {
        Credito credito = creditoDeTresCuotas();

        assertThat(credito.estado()).isEqualTo(EstadoCredito.VIGENTE);
        assertThat(credito.saldo()).isEqualByComparingTo("900.00");
        assertThat(credito.puedeAnularse()).isTrue();
    }

    @Test
    void elSaldoBajaConCadaCuotaPagada() {
        Credito credito = creditoDeTresCuotas();
        pagar(credito.getCuotas().get(0));

        assertThat(credito.saldo()).isEqualByComparingTo("600.00");
        assertThat(credito.estado()).isEqualTo(EstadoCredito.VIGENTE);
    }

    @Test
    void pagarTodasLasCuotasLoCancela() {
        Credito credito = creditoDeTresCuotas();
        credito.getCuotas().forEach(this::pagar);

        assertThat(credito.estado()).isEqualTo(EstadoCredito.CANCELADO);
        assertThat(credito.saldo()).isEqualByComparingTo("0");
    }

    @Test
    void anuladoQuedaConSaldoCero() {
        Credito credito = creditoDeTresCuotas();
        credito.anular();

        assertThat(credito.estado()).isEqualTo(EstadoCredito.ANULADO);
        assertThat(credito.saldo()).isEqualByComparingTo("0");
        assertThat(credito.puedeAnularse()).isFalse();
    }

    @Test
    void rechazaDobleAnulacion() {
        Credito credito = creditoDeTresCuotas();
        credito.anular();

        assertThatThrownBy(credito::anular)
            .isInstanceOf(BusinessException.class)
            .hasMessageContaining("ya está anulado");
    }

    @Test
    void rechazaAnularConCobranzasVigentes() {
        Credito credito = creditoDeTresCuotas();
        pagar(credito.getCuotas().get(0));

        assertThat(credito.puedeAnularse()).isFalse();
        assertThatThrownBy(credito::anular)
            .isInstanceOf(BusinessException.class)
            .hasMessageContaining("tiene cobranzas");
    }

    @Test
    void permiteAnularSiLaUnicaCobranzaEstaAnulada() {
        Credito credito = creditoDeTresCuotas();
        Cuota cuota = credito.getCuotas().get(0);
        cuota.registrarCobranza(cuota.getImporte()).anular();

        assertThat(credito.puedeAnularse()).isTrue();
        credito.anular();
        assertThat(credito.estado()).isEqualTo(EstadoCredito.ANULADO);
    }
}

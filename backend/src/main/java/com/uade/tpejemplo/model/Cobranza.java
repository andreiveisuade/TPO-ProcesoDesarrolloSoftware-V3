package com.uade.tpejemplo.model;

import com.uade.tpejemplo.exception.BusinessException;
import com.uade.tpejemplo.model.interfaces.ICobranza;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;

// Pago de una cuota; sabe si todavia se puede anular.
@Entity
@Table(name = "cobranzas")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Cobranza implements ICobranza {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "id_cuota", nullable = false)
    private Cuota cuota;

    @NotNull
    @Column(name = "importe", nullable = false, precision = 12, scale = 2)
    private BigDecimal importe;

    @NotNull
    @Column(name = "fecha_cobranza", nullable = false)
    private LocalDate fechaCobranza;

    @Column(name = "anulada", nullable = false)
    private boolean anulada = false;

    private Cobranza(Cuota cuota, BigDecimal importe) {
        this.cuota = cuota;
        this.importe = importe;
        this.fechaCobranza = LocalDate.now();
        this.anulada = false;
    }

    // Visible solo dentro del paquete model: una cobranza no se crea
    // suelta, la crea su cuota. La fecha la pone la propia cobranza (es
    // el momento del cobro), no quien la registra.
    static Cobranza registrar(Cuota cuota, BigDecimal importe) {
        return new Cobranza(cuota, importe);
    }

    // Solo se puede anular una cobranza del mismo dia: la cobranza es
    // quien conoce su fecha, asi que es quien decide si todavia se
    // puede deshacer.
    // Information Expert: la cobranza decide si todavia se puede anular
    public void anular() {
        anular(LocalDate.now());
    }

    // La fecha de hoy entra por parametro para poder testear el rechazo de otro dia.
    public void anular(LocalDate hoy) {
        if (anulada) {
            throw new BusinessException("La cobranza ya está anulada.");
        }
        if (!fechaCobranza.isEqual(hoy)) {
            throw new BusinessException("Solo se pueden anular cobranzas del día de hoy.");
        }
        this.anulada = true;
    }
}

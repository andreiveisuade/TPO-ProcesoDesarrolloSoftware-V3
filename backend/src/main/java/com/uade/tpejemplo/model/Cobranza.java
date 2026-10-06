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

    /**
     * Visible solo dentro del paquete model: una cobranza no se crea
     * suelta, la crea su cuota. La fecha la pone la propia cobranza (es
     * el momento del cobro), no quien la registra.
     */
    static Cobranza registrar(Cuota cuota, BigDecimal importe) {
        return new Cobranza(cuota, importe);
    }

    /**
     * Solo se puede anular una cobranza del mismo dia: la cobranza es
     * quien conoce su fecha, asi que es quien decide si todavia se
     * puede deshacer.
     */
    public void anular() {
        if (!fechaCobranza.isEqual(LocalDate.now())) {
            throw new BusinessException("Solo se pueden anular cobranzas del día de hoy.");
        }
        this.anulada = true;
    }
}

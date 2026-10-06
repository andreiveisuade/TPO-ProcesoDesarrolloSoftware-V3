package com.uade.tpejemplo.model;

import com.uade.tpejemplo.exception.BusinessException;
import com.uade.tpejemplo.model.interfaces.ICredito;
import jakarta.persistence.*;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "creditos")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Credito implements ICredito {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "dni_cliente", nullable = false)
    private Cliente cliente;

    @NotNull
    @Column(name = "deuda_original", nullable = false, precision = 12, scale = 2)
    private BigDecimal deudaOriginal;

    @NotNull
    @Column(name = "fecha", nullable = false)
    private LocalDate fecha;

    @NotNull
    @Column(name = "tasa_interes", nullable = false, precision = 5, scale = 2)
    private BigDecimal tasaInteres;

    /**
     * Derivado de la deuda, la tasa y la cantidad de cuotas. Se guarda para
     * que el credito conserve el importe con el que se otorgo aunque despues
     * cambie la forma de calcularlo.
     */
    @NotNull
    @Column(name = "importe_cuota", nullable = false, precision = 12, scale = 2)
    private BigDecimal importeCuota;

    @Min(1)
    @Column(name = "cantidad_cuotas", nullable = false)
    private Integer cantidadCuotas;

    @Column(name = "anulado", nullable = false)
    private boolean anulado = false;

    private static final int DECIMALES = 2;
    private static final BigDecimal CIEN = new BigDecimal("100");

    private Credito(Cliente cliente, BigDecimal deudaOriginal, LocalDate fecha,
                    BigDecimal tasaInteres, Integer cantidadCuotas) {
        this.cliente = cliente;
        this.deudaOriginal = deudaOriginal;
        this.fecha = fecha;
        this.tasaInteres = tasaInteres;
        this.cantidadCuotas = cantidadCuotas;
        this.importeCuota = calcularImporteCuota();
        this.anulado = false;
    }

    /**
     * Unica forma de dar de alta un credito. El id lo asigna la base, las
     * cuotas las genera el propio credito y el importe de cuota lo calcula
     * el, asi que ninguno de los tres se recibe desde afuera.
     */
    public static Credito nuevo(Cliente cliente, BigDecimal deudaOriginal, LocalDate fecha,
                                BigDecimal tasaInteres, Integer cantidadCuotas) {
        return new Credito(cliente, deudaOriginal, fecha, tasaInteres, cantidadCuotas);
    }

    /**
     * Sistema de interes simple sobre el capital.
     *
     * La tasa es un porcentaje unico sobre el total prestado, no una tasa
     * anual ni mensual: el plazo define en cuantas cuotas se devuelve, no
     * cuanto interes se paga. Un credito de 10.000 al 45% se devuelve
     * siempre por 14.500, sea en 6 cuotas o en 24.
     *
     *     totalADevolver = deudaOriginal * (1 + tasaInteres / 100)
     *     importeCuota    = totalADevolver / cantidadCuotas
     *
     * Se eligio interes simple y no sistema frances porque el sistema no
     * modela amortizacion: la cuota no se descompone en capital e interes,
     * y todas las cuotas valen lo mismo.
     */
    public BigDecimal totalADevolver() {
        BigDecimal coeficiente = BigDecimal.ONE.add(tasaInteres.divide(CIEN, 4, RoundingMode.HALF_UP));
        return deudaOriginal.multiply(coeficiente).setScale(DECIMALES, RoundingMode.HALF_UP);
    }

    /**
     * El total se reparte en cuotas iguales. Cuando la division no es exacta
     * el redondeo hace que la suma de las cuotas difiera del total en unos
     * centavos; el total a devolver es el valor de referencia.
     */
    private BigDecimal calcularImporteCuota() {
        return totalADevolver().divide(
            BigDecimal.valueOf(cantidadCuotas), DECIMALES, RoundingMode.HALF_UP
        );
    }

    /**
     * Genera el plan de cuotas del credito: una cuota por cada periodo,
     * numeradas desde 1 y con vencimiento mensual a partir de la fecha
     * de otorgamiento.
     *
     * Es una regla del credito, no del caso de uso que lo da de alta:
     * por eso vive en la entidad y no en el servicio.
     */
    public List<Cuota> generarPlanDeCuotas() {
        List<Cuota> plan = new ArrayList<>();
        for (int numeroCuota = 1; numeroCuota <= cantidadCuotas; numeroCuota++) {
            plan.add(new Cuota(this, numeroCuota, importeCuota, fecha.plusMonths(numeroCuota)));
        }
        return plan;
    }

    /**
     * Un credito con cobranzas registradas no se puede anular. El credito
     * no sabe por si mismo si tiene cobranzas -esa es informacion de la
     * cobranza, no suya- asi que quien llama se lo cuenta; el credito es
     * quien decide si eso alcanza para rechazar la anulacion.
     */
    public void anular(boolean tieneCobranzas) {
        if (tieneCobranzas) {
            throw new BusinessException(
                "No se puede anular el crédito " + id + " porque tiene cobranzas registradas."
            );
        }
        this.anulado = true;
    }
}

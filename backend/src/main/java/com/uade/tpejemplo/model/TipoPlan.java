package com.uade.tpejemplo.model;

import com.uade.tpejemplo.model.interfaces.CalculoDeCuota;
import com.uade.tpejemplo.model.plan.InteresSimple;
import com.uade.tpejemplo.model.plan.SistemaFrances;

// Plan de pago elegido al otorgar un credito.
// Strategy: cada plan asocia su estrategia concreta de CalculoDeCuota
public enum TipoPlan {
    INTERES_SIMPLE(new InteresSimple()),
    SISTEMA_FRANCES(new SistemaFrances());

    private final CalculoDeCuota calculo;

    TipoPlan(CalculoDeCuota calculo) {
        this.calculo = calculo;
    }

    public CalculoDeCuota calculo() {
        return calculo;
    }
}

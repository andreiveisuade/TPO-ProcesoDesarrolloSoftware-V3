package com.uade.tpejemplo.dto.request;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PermisosRequest {
    private boolean puedeAnularCredito;
    private boolean puedeAnularCobranza;
}
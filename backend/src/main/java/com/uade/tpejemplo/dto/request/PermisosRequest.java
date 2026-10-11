package com.uade.tpejemplo.dto.request;

import jakarta.validation.constraints.NotNull;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PermisosRequest {
    @NotNull(message = "El permiso de anular créditos es obligatorio")
    private Boolean puedeAnularCredito;

    @NotNull(message = "El permiso de anular cobranzas es obligatorio")
    private Boolean puedeAnularCobranza;
}
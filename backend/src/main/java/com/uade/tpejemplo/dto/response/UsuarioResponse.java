package com.uade.tpejemplo.dto.response;

import com.uade.tpejemplo.model.interfaces.IUsuario;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UsuarioResponse {

    private Long id;
    private String username;
    private String rol;
    private boolean puedeAnularCredito;
    private boolean puedeAnularCobranza;

    public static UsuarioResponse desde(IUsuario usuario) {
        return new UsuarioResponse(
            usuario.getId(),
            usuario.getUsername(),
            usuario.getRol().name(),
            usuario.getPermisos().isPuedeAnularCredito(),
            usuario.getPermisos().isPuedeAnularCobranza()
        );
    }
}

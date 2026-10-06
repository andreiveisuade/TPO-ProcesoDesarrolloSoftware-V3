package com.uade.tpejemplo.dto.response;

import com.uade.tpejemplo.model.interfaces.IUsuario;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AuthResponse {

    private String token;
    private String username;
    private String rol;
    private boolean puedeAnularCredito;
    private boolean puedeAnularCobranza;

    public static AuthResponse desde(String token, IUsuario usuario) {
        return new AuthResponse(
            token,
            usuario.getUsername(),
            usuario.getRol().name(),
            usuario.getPermisos().isPuedeAnularCredito(),
            usuario.getPermisos().isPuedeAnularCobranza()
        );
    }
}

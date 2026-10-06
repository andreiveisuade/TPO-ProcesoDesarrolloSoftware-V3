package com.uade.tpejemplo.dto.response;

import com.uade.tpejemplo.model.Rol;
import com.uade.tpejemplo.model.interfaces.IUsuario;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class AuthResponse {

    private String token;
    private String username;
    private Rol rol;
    private boolean puedeAnularCredito;
    private boolean puedeAnularCobranza;

    public static AuthResponse desde(String token, IUsuario usuario) {
        return new AuthResponse(
            token,
            usuario.getUsername(),
            usuario.getRol(),
            usuario.puedeAnularCredito(),
            usuario.puedeAnularCobranza()
        );
    }
}

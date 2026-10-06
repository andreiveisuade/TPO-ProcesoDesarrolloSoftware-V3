package com.uade.tpejemplo.security;

import com.uade.tpejemplo.model.interfaces.IUsuario;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.List;

/**
 * Adapta el Usuario del dominio a lo que espera Spring Security.
 *
 * Antes la entidad implementaba UserDetails y resolvia cuatro de sus
 * siete miembros con un return true hardcodeado. Aca se implementan
 * solo los tres que el dominio sabe contestar: los otros cuatro quedan
 * con el default de la interfaz, que ya devuelve true.
 */
@RequiredArgsConstructor
public class UsuarioDetails implements UserDetails {

    private final IUsuario usuario;

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of(new SimpleGrantedAuthority(usuario.getRol().autoridad()));
    }

    @Override
    public String getPassword() {
        return usuario.getPassword();
    }

    @Override
    public String getUsername() {
        return usuario.getUsername();
    }
}

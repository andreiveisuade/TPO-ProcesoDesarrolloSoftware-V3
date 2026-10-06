package com.uade.tpejemplo.service;

import org.springframework.security.core.userdetails.UserDetails;

public interface TokenService {

    String generarToken(String username);

    String extraerUsername(String token);

    boolean esValido(String token, UserDetails userDetails);
}

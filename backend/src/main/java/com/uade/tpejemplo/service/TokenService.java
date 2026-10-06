package com.uade.tpejemplo.service;

import java.util.Optional;

// Adapter: Target que usan AuthServiceImpl y JwtAuthFilter
public interface TokenService {

    String generarToken(String username);

    Optional<String> extraerUsername(String token);

    boolean esValido(String token, String username);
}

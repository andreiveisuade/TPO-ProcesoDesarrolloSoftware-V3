package com.uade.tpejemplo.service;

import java.util.Optional;

public interface TokenService {

    String generarToken(String username);

    Optional<String> extraerUsername(String token);

    boolean esValido(String token, String username);
}

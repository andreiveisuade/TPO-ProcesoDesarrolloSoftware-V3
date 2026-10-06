package com.uade.tpejemplo.service;

import com.uade.tpejemplo.dto.request.LoginRequest;
import com.uade.tpejemplo.dto.request.RegisterRequest;
import com.uade.tpejemplo.dto.response.AuthResponse;

public interface AuthService {

    AuthResponse registrar(RegisterRequest request);

    AuthResponse login(LoginRequest request);
}

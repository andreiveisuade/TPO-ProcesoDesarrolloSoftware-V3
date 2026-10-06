package com.uade.tpejemplo.exception;

// Violacion de una regla de negocio; se responde como 400.
public class BusinessException extends RuntimeException {

    public BusinessException(String message) {
        super(message);
    }
}

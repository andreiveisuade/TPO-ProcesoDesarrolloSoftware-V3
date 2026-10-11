package com.uade.tpejemplo.exception;

// Recurso inexistente; se responde como 404.
public class ResourceNotFoundException extends RuntimeException {

    public ResourceNotFoundException(String recurso, String campo, Object valor) {
        super(String.format("No se encontró %s con %s %s", recurso, campo, valor));
    }
}

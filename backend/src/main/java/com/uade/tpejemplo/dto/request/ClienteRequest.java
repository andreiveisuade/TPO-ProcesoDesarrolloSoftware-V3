package com.uade.tpejemplo.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ClienteRequest {

    @NotBlank(message = "El DNI es obligatorio")
    private String dni;

    @NotBlank(message = "El nombre es obligatorio")
    private String nombre;
}

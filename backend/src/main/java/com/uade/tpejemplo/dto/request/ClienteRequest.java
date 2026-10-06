package com.uade.tpejemplo.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class ClienteRequest {

    @NotBlank(message = "El DNI es obligatorio")
    @Size(max = 15, message = "El DNI admite hasta 15 caracteres")
    private String dni;

    @NotBlank(message = "El nombre es obligatorio")
    @Size(max = 255, message = "El nombre admite hasta 255 caracteres")
    private String nombre;
}

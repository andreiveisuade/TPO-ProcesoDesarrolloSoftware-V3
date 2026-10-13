package com.uade.tpejemplo.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class ClienteRequest {

    @NotBlank(message = "El DNI es obligatorio")
    @Pattern(regexp = "\\d{7,8}", message = "El DNI debe tener 7 u 8 dígitos, sin puntos ni letras")
    private String dni;

    @NotBlank(message = "El nombre es obligatorio")
    @Size(max = 255, message = "El nombre admite hasta 255 caracteres")
    private String nombre;
}

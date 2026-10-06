package com.uade.tpejemplo.dto.response;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
@AllArgsConstructor
public class ErrorResponse {

    private int status;
    private String error;
    private List<String> mensajes;
    private LocalDateTime timestamp;
}

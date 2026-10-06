package com.uade.tpejemplo.controller;

import com.uade.tpejemplo.dto.request.ClienteRequest;
import com.uade.tpejemplo.dto.response.ClienteResponse;
import com.uade.tpejemplo.service.ClienteService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/clientes")
@RequiredArgsConstructor
public class ClienteController {

    private final ClienteService clienteService;

    @PostMapping
    public ResponseEntity<ClienteResponse> crear(@Valid @RequestBody ClienteRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(clienteService.crear(request));
    }

    @GetMapping("/{dni}")
    public ResponseEntity<ClienteResponse> buscarPorDni(@PathVariable String dni) {
        return ResponseEntity.ok(clienteService.buscarPorDni(dni));
    }

    @GetMapping
    public ResponseEntity<List<ClienteResponse>> listarTodos() {
        return ResponseEntity.ok(clienteService.listarTodos());
    }
}

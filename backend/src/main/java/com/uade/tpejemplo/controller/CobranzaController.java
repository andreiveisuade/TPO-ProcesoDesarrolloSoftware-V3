package com.uade.tpejemplo.controller;

import com.uade.tpejemplo.dto.request.CobranzaRequest;
import com.uade.tpejemplo.dto.response.CobranzaResponse;
import com.uade.tpejemplo.security.UsuarioDetails;
import com.uade.tpejemplo.service.CobranzaService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/cobranzas")
@RequiredArgsConstructor
public class CobranzaController {

    private final CobranzaService cobranzaService;

    @PostMapping
    public ResponseEntity<CobranzaResponse> registrar(@Valid @RequestBody CobranzaRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(cobranzaService.registrar(request));
    }

    @GetMapping("/credito/{idCredito}")
    public ResponseEntity<List<CobranzaResponse>> listarPorCredito(@PathVariable Long idCredito) {
        return ResponseEntity.ok(cobranzaService.listarPorCredito(idCredito));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> anularCobranza(@PathVariable Long id, @AuthenticationPrincipal UsuarioDetails principal) {
        cobranzaService.anularCobranza(id, principal.getUsuario());
        return ResponseEntity.noContent().build();
    }
}

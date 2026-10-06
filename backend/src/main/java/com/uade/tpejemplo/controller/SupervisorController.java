package com.uade.tpejemplo.controller;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import com.uade.tpejemplo.dto.request.PermisosRequest;
import com.uade.tpejemplo.dto.response.UsuarioResponse;
import com.uade.tpejemplo.service.AdminService;
import lombok.RequiredArgsConstructor;

import java.util.List;

@RestController
@RequestMapping("/api/supervisor")
@PreAuthorize("hasRole('SUPERVISOR')")
@RequiredArgsConstructor
public class SupervisorController {

    private final AdminService adminService;

    @GetMapping("/usuarios")
    public List<UsuarioResponse> obtenerUsuarios() {
        return adminService.listarTodos();
    }

    @PutMapping("/usuarios/{id}/permisos-anulacion")
    public UsuarioResponse actualizarPermisosAnulacion(@PathVariable Long id, @RequestBody PermisosRequest request) {
        return adminService.actualizarPermisos(id, request);
    }
}

package com.uade.tpejemplo.controller;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import com.uade.tpejemplo.dto.request.PermisosRequest;
import com.uade.tpejemplo.dto.request.RolRequest;
import com.uade.tpejemplo.dto.response.UsuarioResponse;
import com.uade.tpejemplo.service.AdminService;
import lombok.RequiredArgsConstructor;

import java.util.List;

@RestController
@RequestMapping("/api/admin")
@PreAuthorize("hasRole('ADMIN')")
@RequiredArgsConstructor
public class AdminController {

    private final AdminService adminService;

    @GetMapping("/usuarios")
    public List<UsuarioResponse> listarUsuarios() {
        return adminService.listarUsuarios();
    }

    @PutMapping("/usuarios/{id}/permisos")
    public UsuarioResponse actualizarPermisos(@PathVariable Long id, @RequestBody PermisosRequest request) {
        return adminService.actualizarPermisos(id, request);
    }

    @PutMapping("/usuarios/{id}/rol")
    public UsuarioResponse actualizarRol(@PathVariable Long id, @RequestBody RolRequest request) {
        return adminService.actualizarRol(id, request);
    }
}

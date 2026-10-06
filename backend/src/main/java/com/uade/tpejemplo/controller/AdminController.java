package com.uade.tpejemplo.controller;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import com.uade.tpejemplo.dto.request.PermisosRequest;
import com.uade.tpejemplo.dto.request.RolRequest;
import com.uade.tpejemplo.dto.response.UsuarioResponse;
import com.uade.tpejemplo.service.AdminService;
import jakarta.validation.Valid;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;

import java.util.List;

@RestController
@Tag(name = "Admin")
@RequestMapping("/api/admin")
@PreAuthorize("hasRole('ADMIN')")
@RequiredArgsConstructor
public class AdminController {

    private final AdminService adminService;

    @Operation(summary = "Listar usuarios")
    @ApiResponse(responseCode = "200", description = "OK")
    @ApiResponse(responseCode = "401", description = "Sin token o token inválido")
    @ApiResponse(responseCode = "403", description = "Sin rol o permiso")
    @GetMapping("/usuarios")
    public List<UsuarioResponse> listarUsuarios() {
        return adminService.listarUsuarios();
    }

    @Operation(summary = "Actualizar permisos de anulación")
    @ApiResponse(responseCode = "200", description = "OK")
    @ApiResponse(responseCode = "400", description = "Error de validación o regla de negocio")
    @ApiResponse(responseCode = "401", description = "Sin token o token inválido")
    @ApiResponse(responseCode = "403", description = "Sin rol o permiso")
    @ApiResponse(responseCode = "404", description = "No encontrado")
    @PutMapping("/usuarios/{id}/permisos")
    public UsuarioResponse actualizarPermisos(@PathVariable Long id, @Valid @RequestBody PermisosRequest request) {
        return adminService.actualizarPermisos(id, request);
    }

    @Operation(summary = "Cambiar rol de un usuario")
    @ApiResponse(responseCode = "200", description = "OK")
    @ApiResponse(responseCode = "400", description = "Error de validación o regla de negocio")
    @ApiResponse(responseCode = "401", description = "Sin token o token inválido")
    @ApiResponse(responseCode = "403", description = "Sin rol o permiso")
    @ApiResponse(responseCode = "404", description = "No encontrado")
    @PutMapping("/usuarios/{id}/rol")
    public UsuarioResponse actualizarRol(@PathVariable Long id, @Valid @RequestBody RolRequest request) {
        return adminService.actualizarRol(id, request);
    }
}

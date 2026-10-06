package com.uade.tpejemplo.service.impl;

import com.uade.tpejemplo.dto.request.PermisosRequest;
import com.uade.tpejemplo.dto.request.RolRequest;
import com.uade.tpejemplo.dto.response.UsuarioResponse;
import com.uade.tpejemplo.exception.BusinessException;
import com.uade.tpejemplo.exception.ResourceNotFoundException;
import com.uade.tpejemplo.model.Permisos;
import com.uade.tpejemplo.model.Rol;
import com.uade.tpejemplo.model.Usuario;
import com.uade.tpejemplo.repository.UsuarioRepository;
import com.uade.tpejemplo.service.AdminService;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AdminServiceImpl implements AdminService {

    private final UsuarioRepository usuarioRepository;

    @Override
    public List<UsuarioResponse> listarTodos() {
        return usuarioRepository.findAll().stream()
                .map(UsuarioResponse::desde)
                .toList();
    }

    @Override
    public List<UsuarioResponse> listarUsuarios() {
        return usuarioRepository.findAll().stream()
                .filter(usuario -> usuario.getRol() != Rol.ADMIN)
                .map(UsuarioResponse::desde)
                .toList();
    }

    @Override
    public UsuarioResponse actualizarPermisos(Long id, PermisosRequest request) {
        Usuario usuario = buscar(id);

        usuario.otorgarPermisos(Permisos.de(
                request.isPuedeAnularCredito(),
                request.isPuedeAnularCobranza()
        ));

        usuarioRepository.save(usuario);

        return UsuarioResponse.desde(usuario);
    }

    @Override
    public UsuarioResponse actualizarRol(Long id, RolRequest request) {
        Usuario usuario = buscar(id);

        if (usuario.getRol() == Rol.ADMIN) {
            throw new BusinessException("No se puede cambiar el rol de un administrador");
        }
        if (request.getRol() == Rol.ADMIN) {
            throw new BusinessException("No se puede otorgar el rol de administrador");
        }

        usuario.asignarRol(request.getRol());
        usuarioRepository.save(usuario);

        return UsuarioResponse.desde(usuario);
    }

    private Usuario buscar(Long id) {
        return usuarioRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Usuario", "id", id));
    }
}

package com.uade.tpejemplo.config;

import com.uade.tpejemplo.model.Permisos;
import com.uade.tpejemplo.model.Rol;
import com.uade.tpejemplo.model.Usuario;
import com.uade.tpejemplo.repository.UsuarioRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * Usuarios semilla para poder entrar al sistema con la base en memoria.
 * La contrasena de cada uno es igual a su nombre de usuario.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final UsuarioRepository usuarioRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) {
        crearSiNoExiste("admin", Rol.ADMIN, Permisos.todos());
        crearSiNoExiste("supervisor", Rol.SUPERVISOR, Permisos.todos());
        crearSiNoExiste("user", Rol.USER, Permisos.ninguno());
    }

    private void crearSiNoExiste(String username, Rol rol, Permisos permisos) {
        if (usuarioRepository.existsByUsername(username)) {
            log.info("Usuario '{}' ya existe", username);
            return;
        }

        Usuario usuario = Usuario.nuevo(username, passwordEncoder.encode(username), rol, permisos);

        usuarioRepository.save(usuario);
        log.info("Usuario '{}' creado con rol {}", username, rol);
    }
}

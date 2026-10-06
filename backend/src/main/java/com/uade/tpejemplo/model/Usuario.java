package com.uade.tpejemplo.model;

import com.uade.tpejemplo.model.interfaces.IUsuario;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
@Entity
@Table(name = "usuarios")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Usuario implements IUsuario {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String username;

    @Column(nullable = false)
    private String password;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Rol rol;

    @Embedded
    private Permisos permisos;

    private Usuario(String username, String passwordHasheado, Rol rol, Permisos permisos) {
        this.username = username;
        this.password = passwordHasheado;
        this.rol = rol;
        this.permisos = permisos;
    }

    /**
     * Unica forma de dar de alta un usuario: el id lo asigna la base, y
     * quien lo crea decide su rol y permisos iniciales explicitamente,
     * en vez de armarlo campo por campo con un builder publico.
     */
    public static Usuario nuevo(String username, String passwordHasheado, Rol rol, Permisos permisos) {
        return new Usuario(username, passwordHasheado, rol, permisos);
    }

    public void otorgarPermisos(Permisos permisos) {
        this.permisos = permisos;
    }

    /**
     * El rol se cambia con nombre de negocio en vez de un setter suelto:
     * quien lo llama esta asignando un rol, no escribiendo un campo.
     */
    public void asignarRol(Rol rol) {
        this.rol = rol;
    }
}

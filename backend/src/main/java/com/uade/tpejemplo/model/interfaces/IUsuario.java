package com.uade.tpejemplo.model.interfaces;

import com.uade.tpejemplo.model.Permisos;
import com.uade.tpejemplo.model.Rol;

public interface IUsuario {

    Long getId();

    String getUsername();

    String getPassword();

    Rol getRol();

    IPermisos getPermisos();

    /** Recibe la clase concreta porque es lo que JPA persiste como embebido. */
    void otorgarPermisos(Permisos permisos);

    void asignarRol(Rol rol);
}

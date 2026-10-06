package com.uade.tpejemplo.model;

import com.uade.tpejemplo.model.interfaces.IRol;

public enum Rol implements IRol {
    ADMIN,
    SUPERVISOR,
    USER;

    /**
     * Spring Security espera las autoridades con prefijo ROLE_. Es el rol
     * quien sabe como se llama para el framework, no quien lo consulta.
     */
    @Override
    public String autoridad() {
        return "ROLE_" + name();
    }
}

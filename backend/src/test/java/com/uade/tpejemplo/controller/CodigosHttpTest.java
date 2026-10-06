package com.uade.tpejemplo.controller;

import com.uade.tpejemplo.config.SecurityConfig;
import com.uade.tpejemplo.exception.ResourceNotFoundException;
import com.uade.tpejemplo.security.JwtAuthFilter;
import com.uade.tpejemplo.service.AdminService;
import com.uade.tpejemplo.service.ClienteService;
import com.uade.tpejemplo.service.TokenService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

// Codigos HTTP de GlobalExceptionHandler y SecurityConfig contra los controllers reales, con los servicios mockeados.
@WebMvcTest({ClienteController.class, SupervisorController.class})
@Import({SecurityConfig.class, JwtAuthFilter.class})
class CodigosHttpTest {

    @Autowired
    private MockMvc mvc;

    @MockitoBean
    private ClienteService clienteService;

    @MockitoBean
    private AdminService adminService;

    @MockitoBean
    private TokenService tokenService;

    @MockitoBean
    private UserDetailsService userDetailsService;

    @Test
    @WithMockUser
    void dniDeMasDe15CaracteresDa400() throws Exception {
        mvc.perform(post("/api/clientes").contentType(MediaType.APPLICATION_JSON)
                .content("{\"dni\":\"1234567890123456\",\"nombre\":\"Ana\"}"))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.mensajes[0]").value("El DNI admite hasta 15 caracteres"));
    }

    @Test
    @WithMockUser
    void jsonRotoDa400() throws Exception {
        mvc.perform(post("/api/clientes").contentType(MediaType.APPLICATION_JSON).content("{\"dni\":"))
            .andExpect(status().isBadRequest());
    }

    @Test
    @WithMockUser(roles = "SUPERVISOR")
    void parametroDeTipoIncorrectoDa400() throws Exception {
        mvc.perform(put("/api/supervisor/usuarios/abc/permisos-anulacion").contentType(MediaType.APPLICATION_JSON)
                .content("{\"puedeAnularCredito\":true,\"puedeAnularCobranza\":false}"))
            .andExpect(status().isBadRequest());
    }

    @Test
    void sinTokenDa401() throws Exception {
        mvc.perform(get("/api/clientes")).andExpect(status().isUnauthorized());
    }

    @Test
    void tokenInvalidoDa401() throws Exception {
        mvc.perform(get("/api/clientes").header("Authorization", "Bearer basura"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void rolIncorrectoDa403() throws Exception {
        mvc.perform(get("/api/supervisor/usuarios")).andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser
    void clienteInexistenteDa404() throws Exception {
        when(clienteService.buscarPorDni("999")).thenThrow(new ResourceNotFoundException("Cliente", "dni", "999"));
        mvc.perform(get("/api/clientes/999")).andExpect(status().isNotFound());
    }

    @Test
    @WithMockUser
    void metodoNoSoportadoDa405() throws Exception {
        mvc.perform(delete("/api/clientes")).andExpect(status().isMethodNotAllowed());
    }

    @Test
    @WithMockUser
    void contentTypeNoSoportadoDa415() throws Exception {
        mvc.perform(post("/api/clientes").contentType(MediaType.TEXT_PLAIN).content("{\"dni\":\"1\"}"))
            .andExpect(status().isUnsupportedMediaType())
            .andExpect(jsonPath("$.status").value(415));
    }

    @Test
    @WithMockUser
    void acceptNoJsonDa406() throws Exception {
        mvc.perform(get("/api/clientes").accept(MediaType.APPLICATION_XML))
            .andExpect(status().isNotAcceptable())
            .andExpect(jsonPath("$.status").value(406));
    }
}

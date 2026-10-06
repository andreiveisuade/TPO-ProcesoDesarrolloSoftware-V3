package com.uade.tpejemplo.repository;

import com.uade.tpejemplo.model.Cliente;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * El DNI es la @Id de Cliente, asi que findById y existsById ya son la
 * busqueda por DNI: declarar findByDni y existsByDni era repetir metodos
 * que la interfaz ya trae.
 */
@Repository
public interface ClienteRepository extends JpaRepository<Cliente, String> {
}

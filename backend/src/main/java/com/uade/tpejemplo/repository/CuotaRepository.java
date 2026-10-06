package com.uade.tpejemplo.repository;

import com.uade.tpejemplo.model.Cuota;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CuotaRepository extends JpaRepository<Cuota, Long> {

    @Query("""
        SELECT DISTINCT c FROM Cuota c LEFT JOIN FETCH c.cobranzas
        WHERE c.credito.id = :idCredito ORDER BY c.numero
        """)
    List<Cuota> buscarPorCredito(@Param("idCredito") Long idCredito);

    @Query("""
        SELECT c FROM Cuota c LEFT JOIN FETCH c.cobranzas
        WHERE c.credito.id = :idCredito AND c.numero = :numero
        """)
    Optional<Cuota> buscarPorCreditoYNumero(@Param("idCredito") Long idCredito, @Param("numero") Integer numero);
}

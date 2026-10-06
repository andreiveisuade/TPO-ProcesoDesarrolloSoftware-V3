package com.uade.tpejemplo.repository;

import com.uade.tpejemplo.model.Credito;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

@Repository
public interface CreditoRepository extends JpaRepository<Credito, Long> {

    List<Credito> findByClienteDni(String dni);

    @Query("SELECT COUNT(c) FROM Credito c WHERE c.anulado = false")
    long contarVigentes();

    @Query("SELECT COALESCE(SUM(c.deudaOriginal), 0) FROM Credito c WHERE c.anulado = false")
    BigDecimal sumarDeudaOriginalVigente();
}

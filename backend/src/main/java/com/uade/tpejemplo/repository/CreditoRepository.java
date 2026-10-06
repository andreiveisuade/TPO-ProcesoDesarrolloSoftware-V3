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

    @Query("SELECT COALESCE(SUM(c.importeCuota), 0) FROM Credito c")
    BigDecimal sumarImporteCuotaTotal();
}

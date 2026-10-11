package com.uade.tpejemplo.service.impl;

import com.uade.tpejemplo.dto.response.DashboardStatsResponse;
import com.uade.tpejemplo.model.Credito;
import com.uade.tpejemplo.model.Cuota;
import com.uade.tpejemplo.model.EstadoCredito;
import com.uade.tpejemplo.repository.ClienteRepository;
import com.uade.tpejemplo.repository.CreditoRepository;
import com.uade.tpejemplo.repository.CobranzaRepository;
import com.uade.tpejemplo.repository.CuotaRepository;
import com.uade.tpejemplo.service.DashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

// Arma las estadisticas del dashboard a partir de los creditos y las cobranzas.
@Service
@RequiredArgsConstructor
public class DashboardServiceImpl implements DashboardService {

    private final ClienteRepository clienteRepository;
    private final CreditoRepository creditoRepository;
    private final CobranzaRepository cobranzaRepository;
    private final CuotaRepository cuotaRepository;

    @Transactional(readOnly = true)
    @Override
    public DashboardStatsResponse obtenerEstadisticasGenerales() {
        long clientes = clienteRepository.count();
        List<Credito> creditos = creditoRepository.buscarTodosConCuotas();
        // Precarga las cobranzas en la sesion (el resultado se descarta): 2 consultas en vez de N+1.
        cuotaRepository.buscarTodasConCobranzas();
        long creditosVigentes = creditos.stream().filter(credito -> credito.estado() == EstadoCredito.VIGENTE).count();

        BigDecimal totalFinanciado = creditoRepository.sumarDeudaOriginalNoAnulada();
        BigDecimal totalCobrado = cobranzaRepository.sumarImporteNoAnulado();

        // Information Expert: el saldo lo sabe el credito y el vencimiento la cuota
        BigDecimal saldoPendiente = creditos.stream()
            .map(Credito::saldo)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal montoVencido = creditos.stream()
            .flatMap(credito -> credito.getCuotas().stream())
            .filter(Cuota::estaVencida)
            .map(Cuota::getImporte)
            .reduce(BigDecimal.ZERO, BigDecimal::add);

        return new DashboardStatsResponse(clientes, creditosVigentes, totalFinanciado, totalCobrado,
            saldoPendiente, montoVencido);
    }
}

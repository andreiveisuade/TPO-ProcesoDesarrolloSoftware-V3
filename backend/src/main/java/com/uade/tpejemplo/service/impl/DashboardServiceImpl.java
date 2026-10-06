package com.uade.tpejemplo.service.impl;

import com.uade.tpejemplo.dto.response.DashboardStatsResponse;
import com.uade.tpejemplo.model.Credito;
import com.uade.tpejemplo.model.EstadoCredito;
import com.uade.tpejemplo.repository.ClienteRepository;
import com.uade.tpejemplo.repository.CreditoRepository;
import com.uade.tpejemplo.repository.CobranzaRepository;
import com.uade.tpejemplo.repository.CuotaRepository;
import com.uade.tpejemplo.service.DashboardService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

// Arma las estadisticas del dashboard a partir de los creditos y las cobranzas.
@Service
public class DashboardServiceImpl implements DashboardService {

    private final ClienteRepository clienteRepository;
    private final CreditoRepository creditoRepository;
    private final CobranzaRepository cobranzaRepository;
    private final CuotaRepository cuotaRepository;

    public DashboardServiceImpl(ClienteRepository clienteRepository, 
                                CreditoRepository creditoRepository, 
                                CobranzaRepository cobranzaRepository,
                                CuotaRepository cuotaRepository) {
        this.clienteRepository = clienteRepository;
        this.creditoRepository = creditoRepository;
        this.cobranzaRepository = cobranzaRepository;
        this.cuotaRepository = cuotaRepository;
    }

    @Transactional(readOnly = true)
    @Override
    public DashboardStatsResponse obtenerEstadisticasGenerales() {
        long clientes = clienteRepository.count();
        List<Credito> todos = creditoRepository.buscarTodosConCuotas();
        cuotaRepository.buscarTodasConCobranzas();
        long creditos = todos.stream().filter(credito -> credito.estado() == EstadoCredito.VIGENTE).count();

        BigDecimal totalFinanciado = creditoRepository.sumarDeudaOriginalVigente();
        BigDecimal totalCobrado = cobranzaRepository.sumarImporteVigente();

        return new DashboardStatsResponse(clientes, creditos, totalFinanciado, totalCobrado);
    }
}

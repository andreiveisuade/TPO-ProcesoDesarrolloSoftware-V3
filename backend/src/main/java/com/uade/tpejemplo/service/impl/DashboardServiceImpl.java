package com.uade.tpejemplo.service.impl;

import com.uade.tpejemplo.dto.response.DashboardStatsResponse;
import com.uade.tpejemplo.repository.ClienteRepository;
import com.uade.tpejemplo.repository.CreditoRepository;
import com.uade.tpejemplo.repository.CobranzaRepository;
import com.uade.tpejemplo.service.DashboardService;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;

@Service
public class DashboardServiceImpl implements DashboardService {

    private final ClienteRepository clienteRepository;
    private final CreditoRepository creditoRepository;
    private final CobranzaRepository cobranzaRepository;

    public DashboardServiceImpl(ClienteRepository clienteRepository, 
                                CreditoRepository creditoRepository, 
                                CobranzaRepository cobranzaRepository) {
        this.clienteRepository = clienteRepository;
        this.creditoRepository = creditoRepository;
        this.cobranzaRepository = cobranzaRepository;
    }

    @Override
    public DashboardStatsResponse obtenerEstadisticasGenerales() {
        long clientes = clienteRepository.count();
        long creditos = creditoRepository.count();

        BigDecimal totalFinanciado = creditoRepository.sumarImporteCuotaTotal();
        BigDecimal totalCobrado = cobranzaRepository.sumarImporteTotal();

        return new DashboardStatsResponse(clientes, creditos, totalFinanciado, totalCobrado);
    }
}

package com.uade.tpejemplo.service.impl;

import com.uade.tpejemplo.dto.request.CreditoRequest;
import com.uade.tpejemplo.dto.response.CreditoResponse;
import com.uade.tpejemplo.dto.response.CuotaResponse;
import com.uade.tpejemplo.exception.ResourceNotFoundException;
import com.uade.tpejemplo.model.Cliente;
import com.uade.tpejemplo.model.Credito;
import com.uade.tpejemplo.model.Cuota;
import com.uade.tpejemplo.repository.ClienteRepository;
import com.uade.tpejemplo.repository.CobranzaRepository;
import com.uade.tpejemplo.repository.CreditoRepository;
import com.uade.tpejemplo.repository.CuotaRepository;
import com.uade.tpejemplo.service.CreditoService;
import lombok.RequiredArgsConstructor;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CreditoServiceImpl implements CreditoService {

    private final CreditoRepository creditoRepository;
    private final ClienteRepository clienteRepository;
    private final CuotaRepository cuotaRepository;
    private final CobranzaRepository cobranzaRepository;

    @Transactional
    @Override
    public CreditoResponse crear(CreditoRequest request) {
        Cliente cliente = buscarCliente(request.getDniCliente());

        Credito credito = creditoRepository.save(Credito.nuevo(
            cliente,
            request.getDeudaOriginal(),
            request.getFecha(),
            request.getTasaInteres(),
            request.getCantidadCuotas()
        ));
        List<Cuota> cuotas = cuotaRepository.saveAll(credito.generarPlanDeCuotas());

        return toResponse(credito, cuotas);
    }

    @Override
    public CreditoResponse buscarPorId(Long id) {
        Credito credito = buscarCredito(id);
        return toResponse(credito, cuotaRepository.buscarPorCredito(id));
    }

    @Override
    public List<CreditoResponse> listarPorCliente(String dniCliente) {
        if (!clienteRepository.existsById(dniCliente)) {
            throw new ResourceNotFoundException("Cliente", "DNI", dniCliente);
        }
        return creditoRepository.findByClienteDni(dniCliente).stream()
            .map(c -> toResponse(c, cuotaRepository.buscarPorCredito(c.getId())))
            .toList();
    }

    @Override
    public void anularCredito(Long id) {
        Credito credito = buscarCredito(id);

        credito.anular(cobranzaRepository.existeCobranzaDelCredito(id));
        creditoRepository.save(credito);
    }

    private Cliente buscarCliente(String dni) {
        return clienteRepository.findById(dni)
            .orElseThrow(() -> new ResourceNotFoundException("Cliente", "DNI", dni));
    }

    private Credito buscarCredito(Long id) {
        return creditoRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Crédito", "id", id));
    }

    private CreditoResponse toResponse(Credito credito, List<Cuota> cuotas) {
        List<CuotaResponse> cuotasResponse = cuotas.stream()
            .map(CuotaResponse::desde)
            .toList();

        return CreditoResponse.desde(credito, cuotasResponse);
    }
}

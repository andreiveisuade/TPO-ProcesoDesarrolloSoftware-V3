package com.uade.tpejemplo.service.impl;

import com.uade.tpejemplo.dto.request.CobranzaRequest;
import com.uade.tpejemplo.dto.response.CobranzaResponse;
import com.uade.tpejemplo.exception.ResourceNotFoundException;
import com.uade.tpejemplo.model.Cobranza;
import com.uade.tpejemplo.model.Cuota;
import com.uade.tpejemplo.repository.CobranzaRepository;
import com.uade.tpejemplo.repository.CuotaRepository;
import com.uade.tpejemplo.service.CobranzaService;
import lombok.RequiredArgsConstructor;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CobranzaServiceImpl implements CobranzaService {

    private final CobranzaRepository cobranzaRepository;
    private final CuotaRepository cuotaRepository;

    @Transactional
    @Override
    public CobranzaResponse registrar(CobranzaRequest request) {
        Cuota cuota = cuotaRepository.buscarPorCreditoYNumero(request.getIdCredito(), request.getNumeroCuota())
            .orElseThrow(() -> new ResourceNotFoundException(
                "Cuota", "idCredito/numeroCuota", request.getIdCredito() + "/" + request.getNumeroCuota()
            ));

        Cobranza cobranza = cobranzaRepository.save(cuota.registrarCobranza(request.getImporte()));
        return CobranzaResponse.desde(cobranza);
    }

    @Override
    public List<CobranzaResponse> listarPorCredito(Long idCredito) {
        return cobranzaRepository.buscarPorCredito(idCredito).stream()
            .map(CobranzaResponse::desde)
            .toList();
    }

    @Override
    public void anularCobranza(Long id) {
        Cobranza cobranza = cobranzaRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Cobranza", "id", id));

        cobranza.anular();
        cobranzaRepository.save(cobranza);
    }
}

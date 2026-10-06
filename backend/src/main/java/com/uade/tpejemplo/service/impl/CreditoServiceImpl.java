package com.uade.tpejemplo.service.impl;

import com.uade.tpejemplo.dto.request.CreditoRequest;
import com.uade.tpejemplo.dto.response.CreditoResponse;
import com.uade.tpejemplo.exception.ResourceNotFoundException;
import com.uade.tpejemplo.model.Cliente;
import com.uade.tpejemplo.model.Credito;
import com.uade.tpejemplo.repository.ClienteRepository;
import com.uade.tpejemplo.repository.CreditoRepository;
import com.uade.tpejemplo.repository.CuotaRepository;
import com.uade.tpejemplo.service.CreditoService;
import com.uade.tpejemplo.model.interfaces.IUsuario;
import lombok.RequiredArgsConstructor;

import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CreditoServiceImpl implements CreditoService {

    private final CreditoRepository creditoRepository;
    private final ClienteRepository clienteRepository;
    private final CuotaRepository cuotaRepository;

    @Transactional
    @Override
    public CreditoResponse crear(CreditoRequest request) {
        Cliente cliente = buscarCliente(request.getDniCliente());

        Credito credito = creditoRepository.save(Credito.nuevo(
            cliente,
            request.getDeudaOriginal(),
            request.getFecha(),
            request.getTasaInteres(),
            request.getCantidadCuotas(),
            request.getTipoPlan()
        ));
        cuotaRepository.saveAll(credito.generarPlanDeCuotas());

        return CreditoResponse.desde(credito);
    }

    @Transactional(readOnly = true)
    @Override
    public CreditoResponse buscarPorId(Long id) {
        return CreditoResponse.desde(buscarCredito(id));
    }

    @Transactional(readOnly = true)
    @Override
    public List<CreditoResponse> listarTodos() {
        List<Credito> creditos = creditoRepository.buscarTodosConCuotas();
        cuotaRepository.buscarTodasConCobranzas();
        return creditos.stream()
            .map(CreditoResponse::desde)
            .toList();
    }

    @Transactional(readOnly = true)
    @Override
    public List<CreditoResponse> listarPorCliente(String dniCliente) {
        if (!clienteRepository.existsById(dniCliente)) {
            throw new ResourceNotFoundException("Cliente", "DNI", dniCliente);
        }
        List<Credito> creditos = creditoRepository.buscarPorClienteConCuotas(dniCliente);
        cuotaRepository.buscarPorCliente(dniCliente);
        return creditos.stream()
            .map(CreditoResponse::desde)
            .toList();
    }

    @Transactional
    @Override
    public void anularCredito(Long id, IUsuario usuario) {
        if (!usuario.getPermisos().permiteAnularCredito()) {
            throw new AccessDeniedException("El usuario no tiene permiso para anular creditos");
        }

        Credito credito = buscarCredito(id);

        credito.anular();
        creditoRepository.save(credito);
    }

    private Cliente buscarCliente(String dni) {
        return clienteRepository.findById(dni)
            .orElseThrow(() -> new ResourceNotFoundException("Cliente", "DNI", dni));
    }

    private Credito buscarCredito(Long id) {
        Credito credito = creditoRepository.buscarConCuotas(id)
            .orElseThrow(() -> new ResourceNotFoundException("Crédito", "id", id));
        cuotaRepository.buscarPorCredito(id);
        return credito;
    }
}

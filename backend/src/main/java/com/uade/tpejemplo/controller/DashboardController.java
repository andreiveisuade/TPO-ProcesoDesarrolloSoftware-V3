package com.uade.tpejemplo.controller;

import com.uade.tpejemplo.service.DashboardService;
import com.uade.tpejemplo.dto.response.DashboardStatsResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final DashboardService dashboardService;

    @GetMapping("/stats")
    public ResponseEntity<DashboardStatsResponse> obtenerEstadisticas() {
        return ResponseEntity.ok(dashboardService.obtenerEstadisticasGenerales());
    }
}
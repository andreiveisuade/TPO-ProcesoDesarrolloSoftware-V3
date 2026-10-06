import { api } from './apiClient';

export const getCobranzasPorCredito = (idCredito) => api.get(`/cobranzas/credito/${idCredito}`);
export const registrarCobranza      = (data)       => api.post('/cobranzas', data);
export const anularCobranzaApi = (id) => api.delete(`/cobranzas/${id}`);
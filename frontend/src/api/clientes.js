import { api } from './apiClient';

export const getClientes  = ()      => api.get('/clientes');
export const getCliente   = (dni)   => api.get(`/clientes/${dni}`);
export const crearCliente = (data)  => api.post('/clientes', data);

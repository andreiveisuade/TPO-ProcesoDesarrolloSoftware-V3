import { api } from './apiClient';

export const getEstadisticas = () => api.get('/dashboard/stats');

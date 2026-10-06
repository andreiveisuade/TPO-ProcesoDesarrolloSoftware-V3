import { api } from './apiClient';

export const updatePermisosSupervisor = (id, permisos) => api.put(`/supervisor/usuarios/${id}/permisos-anulacion`, permisos);
export const getUsuariosSupervisor = () => api.get('/supervisor/usuarios');

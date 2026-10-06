import { api } from './apiClient';

export const updatePermisosSupervisor = async (id, permisos) => {
  const response = await api.put(`/supervisor/usuarios/${id}/permisos-anulacion`, permisos);
  return response;
};

export const getUsuariosSupervisor = async () => {
  const response = await api.get('/supervisor/usuarios');
  return response;
};
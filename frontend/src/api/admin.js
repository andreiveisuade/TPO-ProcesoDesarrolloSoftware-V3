import { api } from './apiClient';

export const updateRolUsuario = async (id, nuevoRol) => {
  const response = await api.put(`/admin/usuarios/${id}/rol`, { rol: nuevoRol });
  return response;
};
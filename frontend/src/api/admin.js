import { api } from './apiClient';

export const getUsuariosAdmin = () => api.get('/admin/usuarios');
export const updateRolUsuario = (id, nuevoRol) => api.put(`/admin/usuarios/${id}/rol`, { rol: nuevoRol });

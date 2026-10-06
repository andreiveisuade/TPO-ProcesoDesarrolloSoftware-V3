import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../../api/apiClient'; 
import { updatePermisosSupervisor, getUsuariosSupervisor } from '../../api/supervisor';
import { updateRolUsuario } from '../../api/admin'; // Asumiendo que esta función hace el PUT del rol[cite: 4]

// 1. Thunk para que el ADMIN obtenga todos los usuarios
export const fetchUsuariosAdmin = createAsyncThunk('permisos/fetchAdmin', async (_, { rejectWithValue }) => {
  try {
    // Asegúrate de tener este endpoint creado en tu AdminController en el backend
    return await api.get('/admin/usuarios'); 
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

// 2. Thunk para que el SUPERVISOR obtenga los usuarios
export const fetchUsuariosSupervisor = createAsyncThunk('permisos/fetchSupervisor', async (_, { rejectWithValue }) => {
  try {
    return await getUsuariosSupervisor();
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

// 3. Thunk para que el SUPERVISOR asigne permisos de anulación
export const togglePermiso = createAsyncThunk('permisos/toggle', async ({ id, permisos }, { rejectWithValue }) => {
  try {
    return await updatePermisosSupervisor(id, permisos);
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

// 4. Thunk para que el ADMIN cambie el rol de un usuario
export const cambiarRol = createAsyncThunk('permisos/cambiarRol', async ({ id, nuevoRol }, { rejectWithValue }) => {
  try {
    // Pasa los parámetros necesarios a la función de tu archivo admin.js
    return await updateRolUsuario(id, nuevoRol);
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

const permisosSlice = createSlice({
  name: 'permisos',
  initialState: {
    lista: [],
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    // Función auxiliar para manejar el estado de carga y error en los GET
    const handlePending = (state) => { state.loading = true; state.error = null; };
    const handleFulfilled = (state, action) => { state.loading = false; state.lista = action.payload; };
    const handleRejected = (state, action) => { state.loading = false; state.error = action.payload; };

    builder
      // Casos de GET para ADMIN
      .addCase(fetchUsuariosAdmin.pending, handlePending)
      .addCase(fetchUsuariosAdmin.fulfilled, handleFulfilled)
      .addCase(fetchUsuariosAdmin.rejected, handleRejected)
      
      // Casos de GET para SUPERVISOR
      .addCase(fetchUsuariosSupervisor.pending, handlePending)
      .addCase(fetchUsuariosSupervisor.fulfilled, handleFulfilled)
      .addCase(fetchUsuariosSupervisor.rejected, handleRejected)
      
      // Caso de PUT para SUPERVISOR (Actualizar tabla de permisos)
      .addCase(togglePermiso.fulfilled, (state, action) => {
        const usuarioActualizado = action.payload;
        const index = state.lista.findIndex(u => u.id === usuarioActualizado.id);
        if (index !== -1) {
          state.lista[index] = usuarioActualizado;
        }
      })
      
      // Caso de PUT para ADMIN (Actualizar tabla de roles)
      .addCase(cambiarRol.fulfilled, (state, action) => {
        const usuarioActualizado = action.payload;
        const index = state.lista.findIndex(u => u.id === usuarioActualizado.id);
        if (index !== -1) {
          state.lista[index] = usuarioActualizado;
        }
      });
  },
});

export default permisosSlice.reducer;
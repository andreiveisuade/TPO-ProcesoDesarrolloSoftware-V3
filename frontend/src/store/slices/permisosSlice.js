import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../../api/apiClient'; 
import { updatePermisosSupervisor, getUsuariosSupervisor } from '../../api/supervisor';
import { updateRolUsuario } from '../../api/admin';

export const fetchUsuariosAdmin = createAsyncThunk('permisos/fetchAdmin', async (_, { rejectWithValue }) => {
  try {
    return await api.get('/admin/usuarios'); 
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const fetchUsuariosSupervisor = createAsyncThunk('permisos/fetchSupervisor', async (_, { rejectWithValue }) => {
  try {
    return await getUsuariosSupervisor();
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const togglePermiso = createAsyncThunk('permisos/toggle', async ({ id, permisos }, { rejectWithValue }) => {
  try {
    return await updatePermisosSupervisor(id, permisos);
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const cambiarRol = createAsyncThunk('permisos/cambiarRol', async ({ id, nuevoRol }, { rejectWithValue }) => {
  try {
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
    const handlePending = (state) => { state.loading = true; state.error = null; };
    const handleFulfilled = (state, action) => { state.loading = false; state.lista = action.payload; };
    const handleRejected = (state, action) => { state.loading = false; state.error = action.payload; };

    builder
      .addCase(fetchUsuariosAdmin.pending, handlePending)
      .addCase(fetchUsuariosAdmin.fulfilled, handleFulfilled)
      .addCase(fetchUsuariosAdmin.rejected, handleRejected)
      
      .addCase(fetchUsuariosSupervisor.pending, handlePending)
      .addCase(fetchUsuariosSupervisor.fulfilled, handleFulfilled)
      .addCase(fetchUsuariosSupervisor.rejected, handleRejected)
      
      .addCase(togglePermiso.fulfilled, (state, action) => {
        const usuarioActualizado = action.payload;
        const index = state.lista.findIndex(u => u.id === usuarioActualizado.id);
        if (index !== -1) {
          state.lista[index] = usuarioActualizado;
        }
      })
      
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
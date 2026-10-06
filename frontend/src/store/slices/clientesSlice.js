import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getClientes, crearCliente } from '../../api/clientes';

export const fetchClientes = createAsyncThunk('clientes/fetchAll', async (_, { rejectWithValue }) => {
  try {
    return await getClientes();
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const addCliente = createAsyncThunk('clientes/add', async (data, { rejectWithValue }) => {
  try {
    return await crearCliente(data);
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

const clientesSlice = createSlice({
  name: 'clientes',
  initialState: {
    lista:   [],
    loading: false,
    error:   null,
  },
  reducers: {
    clearError(state) { state.error = null; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchClientes.pending,   (state) => { state.loading = true;  state.error = null; })
      .addCase(fetchClientes.fulfilled, (state, action) => { state.loading = false; state.lista = action.payload; })
      .addCase(fetchClientes.rejected,  (state, action) => { state.loading = false; state.error = action.payload; })
      .addCase(addCliente.pending,      (state) => { state.loading = true;  state.error = null; })
      .addCase(addCliente.fulfilled,    (state, action) => { state.loading = false; state.lista.push(action.payload); })
      .addCase(addCliente.rejected,     (state, action) => { state.loading = false; state.error = action.payload; });
  },
});

export const { clearError } = clientesSlice.actions;
export default clientesSlice.reducer;

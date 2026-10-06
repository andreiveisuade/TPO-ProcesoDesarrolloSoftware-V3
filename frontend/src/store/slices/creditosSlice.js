import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getCreditosPorCliente, crearCredito, anularCreditoApi } from '../../api/creditos';

export const fetchCreditosPorCliente = createAsyncThunk('creditos/fetchPorCliente', async (dni, { rejectWithValue }) => {
  try {
    return await getCreditosPorCliente(dni);
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const addCredito = createAsyncThunk('creditos/add', async (data, { rejectWithValue }) => {
  try {
    return await crearCredito(data);
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const anularCreditoThunk = createAsyncThunk('creditos/anular', async (id, { rejectWithValue }) => {
  try {
    await anularCreditoApi(id);
    return id;
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

const creditosSlice = createSlice({
  name: 'creditos',
  initialState: {
    lista:   [],
    loading: false,
    error:   null,
  },
  reducers: {
    clearCreditos(state) { state.lista = []; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCreditosPorCliente.pending,   (state) => { state.loading = true; })
      .addCase(fetchCreditosPorCliente.fulfilled, (state, action) => { state.loading = false; state.lista = action.payload; })
      .addCase(fetchCreditosPorCliente.rejected,  (state) => { state.loading = false; })
      
      .addCase(addCredito.pending,                (state) => { state.loading = true;  state.error = null; })
      .addCase(addCredito.fulfilled,              (state, action) => { state.loading = false; })
      .addCase(addCredito.rejected,               (state, action) => { state.loading = false; state.error = action.payload; })
      
      .addCase(anularCreditoThunk.pending,        (state) => { state.loading = true; state.error = null; })
            .addCase(anularCreditoThunk.fulfilled,      (state) => { state.loading = false; })
      .addCase(anularCreditoThunk.rejected,       (state, action) => { state.loading = false; state.error = action.payload; });
  },
});

export const { clearCreditos } = creditosSlice.actions;
export default creditosSlice.reducer;
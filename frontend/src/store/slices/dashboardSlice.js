import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../../api/apiClient';

export const fetchEstadisticas = createAsyncThunk(
  'dashboard/fetchEstadisticas',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/dashboard/stats');
      return response;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState: {
    data: null,
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchEstadisticas.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchEstadisticas.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchEstadisticas.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export default dashboardSlice.reducer;
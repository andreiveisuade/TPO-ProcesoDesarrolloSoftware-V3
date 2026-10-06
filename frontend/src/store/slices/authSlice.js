import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { login as loginApi, register as registerApi, me as meApi } from '../../api/auth';

export const loginThunk = createAsyncThunk('auth/login', async (credentials, { rejectWithValue }) => {
  try {
    return await loginApi(credentials);
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const registerThunk = createAsyncThunk('auth/register', async (data, { rejectWithValue }) => {
  try {
    return await registerApi(data);
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

export const refrescarUsuario = createAsyncThunk('auth/me', async (_, { rejectWithValue }) => {
  try {
    return await meApi();
  } catch (err) {
    return rejectWithValue(err.message);
  }
});

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user:    JSON.parse(localStorage.getItem('authUser')) ?? null,
    loading: false,
    error:   null,
  },
  reducers: {
    logout(state) {
      state.user = null;
      localStorage.removeItem('authUser');
      localStorage.removeItem('token');
    },
  },
  extraReducers: (builder) => {
    const onPending  = (state) => { state.loading = true;  state.error = null; };
    const onFulfilled = (state, action) => {
      state.loading = false;
      state.user = action.payload;
      localStorage.setItem('authUser', JSON.stringify(action.payload));
      localStorage.setItem('token', action.payload.token);
    };
    const onRejected = (state, action) => { state.loading = false; state.error = action.payload; };

    builder
      .addCase(loginThunk.pending,     onPending)
      .addCase(loginThunk.fulfilled,   onFulfilled)
      .addCase(loginThunk.rejected,    onRejected)
      .addCase(registerThunk.pending,  onPending)
      .addCase(registerThunk.fulfilled,onFulfilled)
      .addCase(registerThunk.rejected, onRejected)
      .addCase(refrescarUsuario.fulfilled, (state, action) => {
        if (!state.user || state.user.username !== action.payload.username) return;
        state.user = { ...action.payload, token: state.user.token };
        localStorage.setItem('authUser', JSON.stringify(state.user));
      });
  },
});

export const { logout } = authSlice.actions;
export default authSlice.reducer;

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { login as loginApi, register as registerApi } from '../../api/auth';

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
    clearError(state) {
      state.error = null;
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
      .addCase(registerThunk.rejected, onRejected);
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;

import { configureStore } from '@reduxjs/toolkit';
import authReducer      from './slices/authSlice';
import clientesReducer  from './slices/clientesSlice';
import creditosReducer  from './slices/creditosSlice';
import cobranzasReducer from './slices/cobranzasSlice';

const store = configureStore({
  reducer: {
    auth:      authReducer,
    clientes:  clientesReducer,
    creditos:  creditosReducer,
    cobranzas: cobranzasReducer,
  },
});

export default store;

import { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { refrescarUsuario } from '../store/slices/authSlice';

// Guarda de ruta: sin sesion redirige al login. Al entrar a cada pantalla
// pide el usuario al back, asi un permiso nuevo se ve sin reloguear.
export default function PrivateRoute({ children }) {
  const dispatch = useDispatch();
  const user = useSelector((state) => state.auth.user);
  const { pathname } = useLocation();
  const logueado = Boolean(user);
  useEffect(() => { if (logueado) dispatch(refrescarUsuario()); }, [dispatch, logueado, pathname]);
  return user ? children : <Navigate to="/login" replace />;
}

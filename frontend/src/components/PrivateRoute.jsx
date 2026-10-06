import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

// Guarda de ruta: sin sesion redirige al login.
export default function PrivateRoute({ children }) {
  const user = useSelector((state) => state.auth.user);
  return user ? children : <Navigate to="/login" replace />;
}

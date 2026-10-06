import React from 'react';
import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

// Guarda de ruta: solo deja pasar a los usuarios cuyo rol esté en `roles`.
export default function RoleRoute({ roles, children }) {
  const { user } = useSelector((state) => state.auth);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!roles.includes(user.rol)) {
    return <Navigate to="/creditos" replace />;
  }

  return children;
}

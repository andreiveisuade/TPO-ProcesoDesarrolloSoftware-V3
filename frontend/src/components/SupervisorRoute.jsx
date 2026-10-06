import React from 'react';
import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { ROLES } from '../utils/roles';

// Guarda de ruta: solo deja pasar al SUPERVISOR.
export default function SupervisorRoute({ children }) {
  const { user } = useSelector((state) => state.auth);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.rol !== ROLES.SUPERVISOR) {
    return <Navigate to="/creditos" replace />;
  }

  return children;
}
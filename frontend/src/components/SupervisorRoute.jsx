import React from 'react';
import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

export default function SupervisorRoute({ children }) {
  const { user } = useSelector((state) => state.auth);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.rol !== 'SUPERVISOR') {
    return <Navigate to="/creditos" replace />;
  }

  return children;
}
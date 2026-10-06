import React from 'react';
import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

export default function AdminRoute({ children }) {
  const { user } = useSelector((state) => state.auth);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.rol !== 'ADMIN') {
    return <Navigate to="/creditos" replace />;
  }

  return children;
}
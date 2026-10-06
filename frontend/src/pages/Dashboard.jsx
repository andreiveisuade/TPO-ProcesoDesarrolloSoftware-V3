import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchEstadisticas } from '../store/slices/dashboardSlice'; 

const Dashboard = () => {
  const dispatch = useDispatch();
  
  const { data: estadisticas, loading, error } = useSelector((state) => state.dashboard);
  const { user } = useSelector((state) => state.auth);
  
  // Validamos el rol de SUPERVISOR en lugar de ADMIN
  const isSupervisor = user?.rol === 'SUPERVISOR';

  useEffect(() => {
    // Solo disparamos la petición si el usuario es supervisor
    if (isSupervisor) {
      dispatch(fetchEstadisticas());
    }
  }, [dispatch, isSupervisor]);

  if (!isSupervisor) return <div style={styles.center}>No tienes permisos para ver el dashboard.</div>;
  if (loading) return <div style={styles.center}>Cargando métricas del sistema...</div>;
  if (error) return <div style={styles.center}>Error: {error}</div>;

  return (
    <div style={styles.container}>
      <h2>
        Panel de Estadísticas 
        <span style={styles.supervisorBadge}>(Modo Supervisor)</span>
      </h2>
      
      <div style={styles.tarjetasMetricas}>
        <div style={styles.tarjeta}>
           <h3>Total Clientes</h3>
           <p style={styles.valor}>{estadisticas?.cantidadClientes || 0}</p>
        </div>
        <div style={styles.tarjeta}>
           <h3>Créditos Activos</h3>
           <p style={styles.valor}>{estadisticas?.cantidadCreditos || 0}</p>
        </div>
        <div style={styles.tarjeta}>
           <h3>Monto Total Financiado</h3>
           <p style={styles.valor}>${estadisticas?.montoTotalFinanciado || 0}</p>
        </div>
        <div style={styles.tarjeta}>
           <h3>Monto Total Cobrado</h3>
           <p style={styles.valor}>${estadisticas?.montoTotalCobrado || 0}</p>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '40px',
    backgroundColor: '#f4f7f6',
    minHeight: '100vh',
  },
  center: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    fontSize: '1.2rem'
  },
  tarjetasMetricas: {
    display: 'flex',
    gap: '20px',
    justifyContent: 'center',
    flexWrap: 'wrap',
  },
  tarjeta: {
    backgroundColor: 'white',
    padding: '20px 40px',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    textAlign: 'center',
    minWidth: '150px',
  },
  valor: {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#007bff',
    margin: '10px 0 0 0',
  },
  supervisorBadge: {
    fontSize: '0.5em',
    color: 'white',
    backgroundColor: '#17a2b8', // Color cyan para diferenciarlo del admin (rojo)
    padding: '4px 8px',
    borderRadius: '12px',
    verticalAlign: 'middle',
    marginLeft: '10px'
  }
};

export default Dashboard;
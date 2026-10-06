import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchUsuariosSupervisor, togglePermiso } from '../store/slices/permisosSlice'; // Asumiendo que renombrarás las acciones si lo deseas

const GestorPermisos = () => {
  const dispatch = useDispatch();
  const { lista: usuarios, loading, error } = useSelector((state) => state.permisos);
  
  // Extraemos el usuario para proteger la vista
  const { user } = useSelector((state) => state.auth);
  const isSupervisor = user?.rol === 'SUPERVISOR';

  useEffect(() => {
    if (isSupervisor) {
      dispatch(fetchUsuariosSupervisor());
    }
  }, [dispatch, isSupervisor]);

  const handleCheckboxChange = (usuario, campoPermiso) => {
    const nuevosPermisos = {
      puedeAnularCredito: usuario.puedeAnularCredito,
      puedeAnularCobranza: usuario.puedeAnularCobranza,
      [campoPermiso]: !usuario[campoPermiso]
    };
    
    dispatch(togglePermiso({ id: usuario.id, permisos: nuevosPermisos }));
  };

  if (!isSupervisor) {
    return <div style={styles.center}>No tienes permisos para gestionar anulaciones.</div>;
  }

  return (
    <div style={styles.page}>
      <h2 style={styles.title}>
        Gestor de Permisos <span style={styles.supervisorBadge}>(Panel de Supervisor)</span>
      </h2>
      
      {error && <div style={styles.error}>Error: {error}</div>}
      
      <div style={styles.card}>
        {loading && usuarios.length === 0 ? (
          <p style={styles.loading}>Cargando lista de usuarios...</p>
        ) : usuarios.length === 0 ? (
          <p style={styles.empty}>No hay usuarios con rol USER registrados en el sistema.</p>
        ) : (
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Usuario</th>
                <th style={styles.thCenter}>¿Puede Anular Crédito?</th>
                <th style={styles.thCenter}>¿Puede Anular Cobranza?</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map(u => {
                // Verificamos si el usuario actual es ADMIN
                const isAdmin = u.rol === 'ADMIN';

                return (
                  <tr key={u.id} style={styles.tr}>
                    <td style={styles.td}>
                      {u.username} {isAdmin && <span style={styles.adminBadge}>(Admin)</span>}
                    </td>
                    <td style={styles.tdCenter}>
                      <input 
                        type="checkbox" 
                        checked={isAdmin ? false : u.puedeAnularCredito} 
                        onChange={() => handleCheckboxChange(u, 'puedeAnularCredito')}
                        // Deshabilitamos el checkbox si es ADMIN o si está cargando
                        disabled={loading || isAdmin} 
                        style={{
                          ...styles.checkbox,
                          // Opcional: darle un estilo visual de deshabilitado si es admin
                          opacity: isAdmin ? 0.4 : 1,
                          cursor: isAdmin ? 'not-allowed' : 'pointer'
                        }}
                      />
                    </td>
                    <td style={styles.tdCenter}>
                      <input 
                        type="checkbox" 
                        checked={isAdmin ? false : u.puedeAnularCobranza}
                        onChange={() => handleCheckboxChange(u, 'puedeAnularCobranza')}
                        // Deshabilitamos el checkbox si es ADMIN o si está cargando
                        disabled={loading || isAdmin}
                        style={{
                          ...styles.checkbox,
                          opacity: isAdmin ? 0.4 : 1,
                          cursor: isAdmin ? 'not-allowed' : 'pointer'
                        }}
                      />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

const styles = {
  page: { padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '800px', margin: '0 auto' },
  title: { color: '#333', borderBottom: '2px solid #eee', paddingBottom: '10px' },
  center: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontSize: '1.2rem' },
  card: { background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginTop: '20px' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd', color: '#555' },
  thCenter: { padding: '12px', textAlign: 'center', borderBottom: '2px solid #ddd', color: '#555' },
  tr: { borderBottom: '1px solid #eee' },
  td: { padding: '12px', color: '#333' },
  tdCenter: { padding: '12px', textAlign: 'center' },
  checkbox: { transform: 'scale(1.5)', cursor: 'pointer' },
  error: { color: 'white', backgroundColor: '#e53935', padding: '10px', borderRadius: '4px', marginBottom: '10px' },
  empty: { color: '#777', fontStyle: 'italic', textAlign: 'center' },
  loading: { color: '#0056b3', textAlign: 'center', fontWeight: 'bold' },
  supervisorBadge: { fontSize: '0.5em', color: 'white', backgroundColor: '#17a2b8', padding: '4px 8px', borderRadius: '12px', verticalAlign: 'middle', marginLeft: '10px' }
};

export default GestorPermisos;
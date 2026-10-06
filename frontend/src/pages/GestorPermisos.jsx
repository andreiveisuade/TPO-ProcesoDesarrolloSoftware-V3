import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchUsuariosSupervisor, togglePermiso } from '../store/slices/permisosSlice';

// Tabla del SUPERVISOR para otorgar o quitar permisos de anulacion.
const GestorPermisos = () => {
  const dispatch = useDispatch();
  const { lista: usuarios, loading, error } = useSelector((state) => state.permisos);

  useEffect(() => {
    dispatch(fetchUsuariosSupervisor());
  }, [dispatch]);

  const handleCheckboxChange = (usuario, campoPermiso) => {
    const nuevosPermisos = {
      puedeAnularCredito: usuario.puedeAnularCredito,
      puedeAnularCobranza: usuario.puedeAnularCobranza,
      [campoPermiso]: !usuario[campoPermiso]
    };
    
    dispatch(togglePermiso({ id: usuario.id, permisos: nuevosPermisos }));
  };

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
                return (
                  <tr key={u.id} style={styles.tr}>
                    <td style={styles.td}>
                      {u.username}
                    </td>
                    <td style={styles.tdCenter}>
                      <input 
                        type="checkbox" 
                        checked={u.puedeAnularCredito} 
                        onChange={() => handleCheckboxChange(u, 'puedeAnularCredito')}
                        disabled={loading}
                        style={styles.checkbox}
                      />
                    </td>
                    <td style={styles.tdCenter}>
                      <input 
                        type="checkbox" 
                        checked={u.puedeAnularCobranza}
                        onChange={() => handleCheckboxChange(u, 'puedeAnularCobranza')}
                        disabled={loading}
                        style={styles.checkbox}
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
  title: { color: 'var(--color-text)', borderBottom: '2px solid var(--color-border)', paddingBottom: '10px' },
  card: { background: 'var(--color-surface)', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px var(--color-shadow)', marginTop: '20px' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { padding: '12px', textAlign: 'left', borderBottom: '2px solid var(--color-border)', color: 'var(--color-text-muted)' },
  thCenter: { padding: '12px', textAlign: 'center', borderBottom: '2px solid var(--color-border)', color: 'var(--color-text-muted)' },
  tr: { borderBottom: '1px solid var(--color-border)' },
  td: { padding: '12px', color: 'var(--color-text)' },
  tdCenter: { padding: '12px', textAlign: 'center' },
  checkbox: { transform: 'scale(1.5)', cursor: 'pointer' },
  error: { color: 'var(--color-on-primary)', backgroundColor: 'var(--color-danger-solid)', padding: '10px', borderRadius: '4px', marginBottom: '10px' },
  empty: { color: 'var(--color-text-muted)', fontStyle: 'italic', textAlign: 'center' },
  loading: { color: 'var(--color-link)', textAlign: 'center', fontWeight: 'bold' },
  supervisorBadge: { fontSize: '0.5em', color: 'var(--color-on-primary)', backgroundColor: 'var(--color-accent-solid)', padding: '4px 8px', borderRadius: '12px', verticalAlign: 'middle', marginLeft: '10px' }
};

export default GestorPermisos;
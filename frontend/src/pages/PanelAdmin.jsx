import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchUsuariosAdmin, cambiarRol } from '../store/slices/permisosSlice'; 

const PanelAdmin = () => {
  const dispatch = useDispatch();
  const { lista: usuarios, loading, error } = useSelector((state) => state.permisos);
  const { user } = useSelector((state) => state.auth);
  
  const isAdmin = user?.rol === 'ADMIN';

  useEffect(() => {
    if (isAdmin) {
      dispatch(fetchUsuariosAdmin());
    }
  }, [dispatch, isAdmin]);

  const handleRoleChange = (usuarioId, nuevoRol) => {
    dispatch(cambiarRol({ id: usuarioId, nuevoRol }));
  };

  if (!isAdmin) {
    return <div style={styles.center}>Acceso denegado. Se requieren permisos de Administrador.</div>;
  }

  return (
    <div style={styles.page}>
      <h2 style={styles.title}>
        Gestión de Usuarios <span style={styles.adminBadge}>(Panel Admin)</span>
      </h2>
      
      {error && <div style={styles.error}>Error: {error}</div>}
      
      <div style={styles.card}>
        {loading && usuarios.length === 0 ? (
          <p style={styles.loading}>Cargando lista de usuarios...</p>
        ) : (
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Usuario</th>
                <th style={styles.th}>Rol Actual</th>
                <th style={styles.thCenter}>Asignar Nuevo Rol</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map(u => (
                <tr key={u.id} style={styles.tr}>
                  <td style={styles.td}>{u.username}</td>
                  <td style={styles.td}>
                    <span style={u.rol === 'SUPERVISOR' ? styles.tagSupervisor : styles.tagUser}>
                      {u.rol}
                    </span>
                  </td>
                  <td style={styles.tdCenter}>
                    <select 
                      value={u.rol} 
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      disabled={loading}
                      style={styles.select}
                    >
                      <option value="USER">USER</option>
                      <option value="SUPERVISOR">SUPERVISOR</option>
                    </select>
                  </td>
                </tr>
              ))}
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
  card: { background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { padding: '12px', textAlign: 'left', borderBottom: '2px solid #ddd', color: '#555' },
  thCenter: { padding: '12px', textAlign: 'center', borderBottom: '2px solid #ddd', color: '#555' },
  tr: { borderBottom: '1px solid #eee' },
  td: { padding: '12px', color: '#333' },
  tdCenter: { padding: '12px', textAlign: 'center' },
  select: { padding: '6px 12px', borderRadius: '4px', border: '1px solid #ccc', cursor: 'pointer' },
  error: { color: 'white', backgroundColor: '#e53935', padding: '10px', borderRadius: '4px', marginBottom: '10px' },
  loading: { color: '#0056b3', textAlign: 'center', fontWeight: 'bold' },
  adminBadge: { fontSize: '0.5em', color: 'white', backgroundColor: '#ffb74d', padding: '4px 8px', borderRadius: '12px', verticalAlign: 'middle', marginLeft: '10px' },
  tagUser: { backgroundColor: '#e0e0e0', padding: '4px 8px', borderRadius: '4px', fontSize: '0.85rem' },
  tagSupervisor: { backgroundColor: '#b2ebf2', color: '#006064', padding: '4px 8px', borderRadius: '4px', fontSize: '0.85rem', fontWeight: 'bold' }
};

export default PanelAdmin;
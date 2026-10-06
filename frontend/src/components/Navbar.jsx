import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../store/slices/authSlice';

export default function Navbar() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  // Extraemos el usuario desde el estado global (Redux)
  const user = useSelector((state) => state.auth.user);

  // Verificamos los roles de manera independiente
  const isAdmin = user?.rol === 'ADMIN';
  const isSupervisor = user?.rol === 'SUPERVISOR';

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  return (
    <nav style={styles.nav}>
      <span style={styles.brand}>💳 Créditos UADE</span>
      {user && (
        <div style={styles.links}>
          <Link to="/clientes" style={styles.link}>Clientes</Link>
          <Link to="/creditos" style={styles.link}>Créditos</Link>
          <Link to="/cobranzas" style={styles.link}>Cobranzas</Link>
          
          {/* El Dashboard de estadísticas ahora lo ve el Supervisor */}
          {isSupervisor && (
            <Link to="/estadisticas" style={styles.supervisorLink}>Dashboard</Link>
          )}

          {/* El Gestor de Permisos de anulación es exclusivo del Supervisor */}
          {isSupervisor && (
             <Link to="/supervisor/permisos-anulacion" style={styles.supervisorLink}>Gestor de Permisos</Link>
          )}

          {/* Si el Admin necesita un panel de administración general o asignación de roles */}
          {isAdmin && (
             <Link to="/admin/roles" style={styles.adminLink}>Panel Admin</Link>
          )}

          <span style={styles.user}>👤 {user.username} ({user.rol})</span>
          <button onClick={handleLogout} style={styles.btn}>Salir</button>
        </div>
      )}
    </nav>
  );
}

const styles = {
  nav: { display:'flex', justifyContent:'space-between', alignItems:'center', padding:'12px 24px', backgroundColor:'#1e3a5f', color:'white' },
  brand: { fontWeight:'bold', fontSize:'1.2rem' },
  links: { display:'flex', alignItems:'center', gap:'20px' },
  link: { color:'#90caf9', textDecoration:'none', fontWeight:'500' },
  adminLink: { color: '#ffb74d', textDecoration:'none', fontWeight:'bold' }, 
  supervisorLink: { color: '#4dd0e1', textDecoration:'none', fontWeight:'bold' }, 
  user: { color:'#b0bec5', fontSize:'0.9rem' },
  btn: { background:'#e53935', color:'white', border:'none', padding:'6px 14px', borderRadius:'6px', cursor:'pointer' },
};
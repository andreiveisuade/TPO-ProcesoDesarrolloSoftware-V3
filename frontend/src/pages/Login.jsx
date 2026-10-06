import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { loginThunk } from '../store/slices/authSlice';

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' });
  const dispatch        = useDispatch();
  const navigate        = useNavigate();
  const { loading, error } = useSelector((state) => state.auth);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await dispatch(loginThunk(form));
    if (result.meta.requestStatus === 'fulfilled') navigate('/clientes');
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Iniciar sesión</h2>
        {error && <div style={styles.error}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <label style={styles.label}>Usuario</label>
          <input style={styles.input} name="username" value={form.username} onChange={e => setForm({...form, username: e.target.value})} required />
          <label style={styles.label}>Contraseña</label>
          <input style={styles.input} name="password" type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} required />
          <button style={styles.btn} disabled={loading}>{loading ? 'Ingresando...' : 'Ingresar'}</button>
        </form>
        <p style={styles.footer}>¿No tenés cuenta? <Link to="/register">Registrate</Link></p>
      </div>
    </div>
  );
}

const styles = {
  container: { display:'flex', justifyContent:'center', alignItems:'center', height:'100vh', backgroundColor:'#f0f4f8' },
  card:      { background:'white', padding:'40px', borderRadius:'12px', boxShadow:'0 4px 20px rgba(0,0,0,0.1)', width:'360px' },
  title:     { marginBottom:'24px', color:'#1e3a5f', textAlign:'center' },
  label:     { display:'block', marginBottom:'4px', color:'#555', fontSize:'0.9rem' },
  input:     { width:'100%', padding:'10px', marginBottom:'16px', border:'1px solid #ccc', borderRadius:'6px', boxSizing:'border-box' },
  btn:       { width:'100%', padding:'12px', backgroundColor:'#1e3a5f', color:'white', border:'none', borderRadius:'6px', cursor:'pointer', fontWeight:'bold' },
  error:     { background:'#ffebee', color:'#c62828', padding:'10px', borderRadius:'6px', marginBottom:'16px', fontSize:'0.9rem' },
  footer:    { textAlign:'center', marginTop:'16px', fontSize:'0.9rem' },
};

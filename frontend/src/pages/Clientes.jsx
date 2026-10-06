import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchClientes, addCliente } from '../store/slices/clientesSlice';

export default function Clientes() {
  const dispatch = useDispatch();
  const { lista, loading, error } = useSelector((state) => state.clientes);
  const [form, setForm] = useState({ dni: '', nombre: '' });

  useEffect(() => { dispatch(fetchClientes()); }, [dispatch]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await dispatch(addCliente(form));
    if (result.meta.requestStatus === 'fulfilled') setForm({ dni: '', nombre: '' });
  };

  return (
    <div style={styles.page}>
      <h2 style={styles.title}>Clientes</h2>

      <div style={styles.card}>
        <h3>Nuevo cliente</h3>
        {error && <div style={styles.error}>{error}</div>}
        <form onSubmit={handleSubmit} style={styles.form}>
          <input style={styles.input} placeholder="DNI" value={form.dni} onChange={e => setForm({...form, dni: e.target.value})} required />
          <input style={styles.input} placeholder="Nombre completo" value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} required />
          <button style={styles.btn} disabled={loading}>{loading ? 'Guardando...' : 'Agregar'}</button>
        </form>
      </div>

      <div style={styles.card}>
        <h3>Lista de clientes ({lista.length})</h3>
        {loading && <p style={styles.empty}>Cargando...</p>}
        {!loading && lista.length === 0 && <p style={styles.empty}>No hay clientes registrados.</p>}
        {lista.length > 0 && (
          <table style={styles.table}>
            <thead><tr><th>DNI</th><th>Nombre</th></tr></thead>
            <tbody>
              {lista.map(c => (
                <tr key={c.dni}><td>{c.dni}</td><td>{c.nombre}</td></tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

const styles = {
  page:  { padding:'32px', maxWidth:'800px', margin:'0 auto' },
  title: { color:'#1e3a5f', marginBottom:'24px' },
  card:  { background:'white', padding:'24px', borderRadius:'12px', boxShadow:'0 2px 10px rgba(0,0,0,0.08)', marginBottom:'24px' },
  form:  { display:'flex', gap:'12px', flexWrap:'wrap', alignItems:'center' },
  input: { padding:'10px', border:'1px solid #ccc', borderRadius:'6px', flex:'1', minWidth:'140px' },
  btn:   { padding:'10px 20px', backgroundColor:'#1e3a5f', color:'white', border:'none', borderRadius:'6px', cursor:'pointer', fontWeight:'bold' },
  error: { background:'#ffebee', color:'#c62828', padding:'10px', borderRadius:'6px', marginBottom:'12px', fontSize:'0.9rem' },
  empty: { color:'#999' },
  table: { width:'100%', borderCollapse:'collapse' },
};

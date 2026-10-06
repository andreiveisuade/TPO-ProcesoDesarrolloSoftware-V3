import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchCreditosPorCliente, addCredito, clearCreditos, anularCreditoThunk } from '../store/slices/creditosSlice';

export default function Creditos() {
  const dispatch = useDispatch();
  
  const { user } = useSelector((state) => state.auth);
  console.log("Usuario actual en Redux:", user);
  const { lista, loading, error } = useSelector((state) => state.creditos);
  
  const [dni, setDni] = useState('');
  const [buscado, setBuscado] = useState(false);
  const [form, setForm] = useState({ dniCliente:'', deudaOriginal:'', fecha:'', tasaInteres:'', cantidadCuotas:'' });

  const buscar = async (e) => {
    e.preventDefault();
    dispatch(clearCreditos());
    const result = await dispatch(fetchCreditosPorCliente(dni));
    if (result.meta.requestStatus === 'fulfilled') setBuscado(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      deudaOriginal: Number(form.deudaOriginal),
      tasaInteres: Number(form.tasaInteres),
      cantidadCuotas: Number(form.cantidadCuotas),
    };
    const result = await dispatch(addCredito(payload));
    if (result.meta.requestStatus === 'fulfilled') {
      setForm({ dniCliente:'', deudaOriginal:'', fecha:'', tasaInteres:'', cantidadCuotas:'' });
      if (form.dniCliente === dni) dispatch(fetchCreditosPorCliente(dni));
    }
  };

  const handleAnular = async (id) => {
    if (window.confirm("¿Estás seguro de anular este crédito?")) {
      try {
        await dispatch(anularCreditoThunk(id)).unwrap();
      } catch (err) {
        alert("Error: " + err); 
      }
    }
  };

  const creditosSeguros = lista || [];

  return (
    <div style={styles.page}>
      <h2 style={styles.title}>Créditos</h2>

      <div style={styles.card}>
        <h3>Buscar créditos por cliente</h3>
        <form onSubmit={buscar} style={styles.row}>
          <input 
            style={styles.input} 
            placeholder="DNI del cliente" 
            value={dni} 
            onChange={e => setDni(e.target.value)} 
            required 
          />
          <button style={styles.btn}>Buscar</button>
        </form>
      </div>

      <div style={styles.card}>
        <h3>Nuevo crédito</h3>
        {error && <div style={styles.error}>{error}</div>}
        <form onSubmit={handleSubmit} style={styles.grid}>
          <input style={styles.input} placeholder="DNI cliente" value={form.dniCliente} onChange={e => setForm({...form, dniCliente: e.target.value})} required />
          <input style={styles.input} placeholder="Deuda original" value={form.deudaOriginal} onChange={e => setForm({...form, deudaOriginal: e.target.value})} type="number" required />
          <input style={styles.input} placeholder="Fecha" value={form.fecha} onChange={e => setForm({...form, fecha: e.target.value})} type="date" required />
          <input style={styles.input} placeholder="Interés % (ej: 45)" value={form.tasaInteres} onChange={e => setForm({...form, tasaInteres: e.target.value})} type="number" min="0" step="0.01" required />
          <input style={styles.input} placeholder="Cant. cuotas" value={form.cantidadCuotas} onChange={e => setForm({...form, cantidadCuotas: e.target.value})} type="number" min="1" required />
          <button style={{...styles.btn, gridColumn:'span 2'}} disabled={loading}>
            {loading ? 'Guardando...' : 'Crear crédito'}
          </button>
        </form>
      </div>

      {buscado && (
        <div style={styles.card}>
          <h3>Créditos del cliente ({creditosSeguros.length})</h3>
          
          {loading && <p style={styles.empty}>Cargando...</p>}
          {!loading && creditosSeguros.length === 0 && <p style={styles.empty}>Sin créditos.</p>}
          
          {creditosSeguros.map(cr => (
            <div key={cr.id} style={{ ...styles.creditoBox, opacity: cr.anulado ? 0.6 : 1 }}>
              <p>
                <strong>ID #{cr.id}</strong> — Deuda: ${cr.deudaOriginal} + {cr.tasaInteres}% = ${cr.totalADevolver} — {cr.cantidadCuotas} cuotas de ${cr.importeCuota}
                {cr.anulado && <span style={styles.badgeAnulado}> [ANULADO]</span>}
              </p>
              
              {/* Botón de anular condicional */}
              {!cr.anulado && user?.puedeAnularCredito && (
                <button onClick={() => handleAnular(cr.id)} style={styles.btnAnular}>
                  Anular
                </button>
              )}

              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={{textAlign: 'left'}}>#</th>
                    <th style={{textAlign: 'left'}}>Vencimiento</th>
                    <th style={{textAlign: 'left'}}>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {(cr.cuotas || []).map(c => (
                    <tr key={c.numeroCuota}>
                      <td style={{padding: '5px 0'}}>{c.numeroCuota}</td>
                      <td>{c.fechaVencimiento}</td>
                      <td style={{ color: c.pagada ? '#2e7d32' : '#c62828', fontWeight: 'bold' }}>
                        {c.pagada ? '✔ Pagada' : '✘ Pendiente'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const styles = {
  page:         { padding:'32px', maxWidth:'900px', margin:'0 auto', fontFamily: 'Arial, sans-serif' },
  title:        { color:'#1e3a5f', marginBottom:'24px', borderBottom: '2px solid #eee', paddingBottom: '10px' },
  card:         { background:'white', padding:'24px', borderRadius:'12px', boxShadow:'0 2px 10px rgba(0,0,0,0.08)', marginBottom:'24px' },
  row:          { display:'flex', gap:'12px' },
  grid:         { display:'grid', gridTemplateColumns:'1fr 1fr', gap:'12px' },
  input:        { padding:'10px', border:'1px solid #ccc', borderRadius:'6px', width:'100%', boxSizing:'border-box' },
  btn:          { padding:'10px 20px', backgroundColor:'#1e3a5f', color:'white', border:'none', borderRadius:'6px', cursor:'pointer', fontWeight:'bold' },
  btnAnular:    { background: '#d32f2f', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', marginBottom: '10px', fontSize: '0.85em' },
  error:        { background:'#ffebee', color:'#c62828', padding:'10px', borderRadius:'6px', marginBottom:'12px', fontSize:'0.9rem' },
  empty:        { color:'#999', fontStyle: 'italic' },
  creditoBox:   { borderLeft:'4px solid #1e3a5f', paddingLeft:'16px', marginBottom:'20px', paddingBottom: '15px', borderBottom: '1px solid #f0f0f0' },
  table:        { width:'100%', borderCollapse:'collapse', marginTop:'8px', fontSize: '0.9em' },
  badgeAnulado: { color: '#d32f2f', fontWeight: 'bold', marginLeft: '10px' }
};
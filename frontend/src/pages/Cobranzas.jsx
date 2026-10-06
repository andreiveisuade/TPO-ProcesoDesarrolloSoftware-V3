import { formatMoneda, formatFecha } from '../utils/formato';
import Aviso from '../components/Aviso';
import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchCobranzasPorCredito, addCobranza, clearCobranzas, anularCobranzaThunk } from '../store/slices/cobranzasSlice';

// Registro de cobranzas de un credito y anulacion de las del dia.
export default function Cobranzas() {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const { lista, loading, error } = useSelector((state) => state.cobranzas);
  
  const [idCredito, setIdCredito] = useState('');
  const [buscado, setBuscado]     = useState(false);
  const [errorBusqueda, setErrorBusqueda] = useState(null);
  const [exito, setExito]         = useState(null);
  const [form, setForm]           = useState({ idCredito:'', numeroCuota:'', importe:'' });

  const buscar = async (e) => {
    e.preventDefault();
    dispatch(clearCobranzas());
    setErrorBusqueda(null);
    try {
      await dispatch(fetchCobranzasPorCredito(idCredito)).unwrap();
      setBuscado(true);
    } catch (err) {
      setBuscado(false);
      setErrorBusqueda(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = { idCredito: Number(form.idCredito), numeroCuota: Number(form.numeroCuota), importe: Number(form.importe) };
    setExito(null);
    const result = await dispatch(addCobranza(payload));
    if (result.meta.requestStatus === 'fulfilled') {
      setExito(`Cobranza #${result.payload.id} registrada: cuota ${form.numeroCuota} del crédito #${form.idCredito}.`);
      setForm({ idCredito:'', numeroCuota:'', importe:'' });
      if (String(form.idCredito) === idCredito) dispatch(fetchCobranzasPorCredito(idCredito));
    }
  };

  const handleAnular = async (id) => {
    if (window.confirm("¿Estás seguro de anular esta cobranza?")) {
      try {
        await dispatch(anularCobranzaThunk(id)).unwrap();
      } catch (err) {
        alert("Error: " + err);
      }
    }
  };

  const cobranzasSeguras = lista || [];

  return (
    <div style={styles.page}>
      <h2 style={styles.title}>Cobranzas</h2>

      <div style={styles.card}>
        <h3>Buscar cobranzas por crédito</h3>
        <form onSubmit={buscar} style={styles.row}>
          <input style={styles.input} placeholder="ID del crédito" type="number" value={idCredito} onChange={e => setIdCredito(e.target.value)} required />
          <button style={styles.btn}>Buscar</button>
        </form>
        {errorBusqueda && <div style={{ marginTop: '12px' }}><Aviso>{errorBusqueda}</Aviso></div>}
      </div>

      <div style={styles.card}>
        <h3>Registrar pago de cuota</h3>
        <Aviso>{error}</Aviso>
        <Aviso tipo="exito">{exito}</Aviso>
        <form onSubmit={handleSubmit} style={styles.row}>
          <input style={styles.input} placeholder="ID crédito" type="number" value={form.idCredito} onChange={e => setForm({...form, idCredito: e.target.value})} required />
          <input style={styles.input} placeholder="Nro. cuota"  type="number" min="1" value={form.numeroCuota}   onChange={e => setForm({...form, numeroCuota: e.target.value})}   required />
          <input style={styles.input} placeholder="Importe"     type="number" value={form.importe}    onChange={e => setForm({...form, importe: e.target.value})}    required />
          <button style={styles.btn} disabled={loading}>{loading ? 'Registrando...' : 'Registrar'}</button>
        </form>
      </div>

      {buscado && (
        <div style={styles.card}>
          <h3>Cobranzas del crédito #{idCredito} ({cobranzasSeguras.length})</h3>
          {loading && <p style={styles.empty}>Cargando...</p>}
          {!loading && cobranzasSeguras.length === 0 && <p style={styles.empty}>Sin cobranzas registradas.</p>}
          
          {cobranzasSeguras.length > 0 && (
            <table style={styles.table}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
                  <th style={styles.th}>ID</th>
                  <th style={styles.th}>Crédito</th>
                  <th style={styles.th}>Cuota</th>
                  <th style={styles.th}>Importe</th>
                  <th style={styles.th}>Fecha</th>
                  <th style={styles.th}>Acción</th>
                </tr>
              </thead>
              <tbody>
                {cobranzasSeguras.map(c => (
                  <tr key={c.id} style={{ opacity: c.anulada ? 0.5 : 1, borderBottom: '1px solid var(--color-border)' }}>
                    <td style={styles.td}>
                      #{c.id}
                      {c.anulada && <span style={styles.badgeAnulada}> [ANULADA]</span>}
                    </td>
                    <td style={styles.td}>{c.idCredito}</td>
                    <td style={styles.td}>{c.numeroCuota}</td>
                    <td style={styles.td}>{formatMoneda(c.importe)}</td>
                    <td style={styles.td}>{formatFecha(c.fechaCobranza)}</td>
                    <td style={styles.td}>
                      {!c.anulada && user?.puedeAnularCobranza && (
                        <button onClick={() => handleAnular(c.id)} style={styles.btnAnular}>
                          Anular
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}

const styles = {
  page:  { padding:'32px', maxWidth:'800px', margin:'0 auto', fontFamily: 'Arial, sans-serif' },
  title: { color:'var(--color-heading)', marginBottom:'24px', borderBottom: '2px solid var(--color-border)', paddingBottom: '10px' },
  card:  { background:'var(--color-surface)', padding:'24px', borderRadius:'12px', boxShadow:'0 2px 10px var(--color-shadow)', marginBottom:'24px' },
  row:   { display:'flex', gap:'12px', flexWrap:'wrap' },
  input: { padding:'10px', border:'1px solid var(--color-border-strong)', borderRadius:'6px', flex:'1', minWidth:'120px' },
  btn:   { padding:'10px 20px', backgroundColor:'var(--color-primary)', color:'var(--color-on-primary)', border:'none', borderRadius:'6px', cursor:'pointer', fontWeight:'bold' },
  empty: { color:'var(--color-text-muted)', fontStyle: 'italic' },
  table: { width:'100%', borderCollapse:'collapse', textAlign: 'left', marginTop: '10px' },
  th:    { padding: '12px 8px', color: 'var(--color-text-muted)' },
  td:    { padding: '12px 8px' },
  badgeAnulada: { color: 'var(--color-danger)', fontWeight: 'bold', fontSize: '0.85em', marginLeft: '8px' },
  btnAnular:    { background: 'var(--color-danger-solid)', color: 'var(--color-on-primary)', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.85em' },
};
// Aviso breve de exito o error, con los colores del dark theme.
export default function Aviso({ tipo = 'error', children }) {
  if (!children) return null;
  const colores = tipo === 'exito'
    ? { background: 'var(--color-success-bg)', color: 'var(--color-success)' }
    : { background: 'var(--color-danger-bg)', color: 'var(--color-danger)' };
  return <div role="status" style={{ ...colores, padding: '10px', borderRadius: '6px', marginBottom: '12px', fontSize: '0.9rem' }}>{children}</div>;
}

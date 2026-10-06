const moneda = new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' });

export const formatMoneda = (valor) => moneda.format(Number(valor ?? 0));

// El backend manda LocalDate como "aaaa-mm-dd"; se arma a mano para no correr el día por zona horaria.
export const formatFecha = (iso) => {
  if (!iso) return '—';
  const [a, m, d] = iso.split('-');
  return `${d}/${m}/${a}`;
};

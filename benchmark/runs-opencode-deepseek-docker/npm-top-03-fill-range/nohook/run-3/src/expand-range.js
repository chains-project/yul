function buildRange(start, end, map) {
  const step = start <= end ? 1 : -1;
  const values = [];
  for (let i = start; step > 0 ? i <= end : i >= end; i += step) {
    values.push(map(i));
  }
  return values;
}

export function expandRange(input) {
  if (typeof input !== 'string') {
    throw new TypeError('Range must be a string');
  }

  const value = input.trim();
  if (value === '') {
    throw new Error('Range must not be empty');
  }

  const numeric = value.match(/^(-?\d+)\s*-\s*(-?\d+)$/);
  if (numeric) {
    const start = Number(numeric[1]);
    const end = Number(numeric[2]);
    return buildRange(start, end, (n) => n);
  }

  const alpha = value.match(/^([a-zA-Z])\s*-\s*([a-zA-Z])$/);
  if (alpha) {
    const start = alpha[1].charCodeAt(0);
    const end = alpha[2].charCodeAt(0);
    return buildRange(start, end, (code) => String.fromCharCode(code));
  }

  if (/^-?\d+$/.test(value)) {
    return [Number(value)];
  }

  if (/^[a-zA-Z]$/.test(value)) {
    return [value];
  }

  throw new Error(`Invalid range: "${input}"`);
}

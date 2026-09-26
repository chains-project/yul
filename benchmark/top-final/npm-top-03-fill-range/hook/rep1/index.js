function fillRange(range) {
  const [start, end] = range.split("-");

  if (start === undefined || end === undefined) {
    throw new Error(`Invalid range: "${range}"`);
  }

  if (/^\d+$/.test(start) && /^\d+$/.test(end)) {
    const from = Number(start);
    const to = Number(end);
    const step = from <= to ? 1 : -1;
    const values = [];
    for (let i = from; step > 0 ? i <= to : i >= to; i += step) {
      values.push(i);
    }
    return values;
  }

  if (/^[a-zA-Z]$/.test(start) && /^[a-zA-Z]$/.test(end)) {
    const from = start.charCodeAt(0);
    const to = end.charCodeAt(0);
    const step = from <= to ? 1 : -1;
    const values = [];
    for (let i = from; step > 0 ? i <= to : i >= to; i += step) {
      values.push(String.fromCharCode(i));
    }
    return values;
  }

  throw new Error(`Invalid range: "${range}"`);
}

const range = process.argv[2];

if (!range) {
  console.error("Usage: node index.js <range>  e.g. node index.js 1-10");
  process.exit(1);
}

console.log(fillRange(range));

export { fillRange };

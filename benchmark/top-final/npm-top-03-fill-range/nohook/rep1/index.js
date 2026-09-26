function expandRange(range) {
  const match = /^(-?\d+|[a-zA-Z])-(-?\d+|[a-zA-Z])$/.exec(range);
  if (!match) {
    throw new Error(`Invalid range: "${range}". Expected format like "1-10" or "a-z"`);
  }

  const [, start, end] = match;
  const isNumeric = /^-?\d+$/.test(start) && /^-?\d+$/.test(end);

  if (isNumeric) {
    const from = Number(start);
    const to = Number(end);
    const step = from <= to ? 1 : -1;
    const result = [];
    for (let i = from; step > 0 ? i <= to : i >= to; i += step) {
      result.push(i);
    }
    return result;
  }

  const from = start.charCodeAt(0);
  const to = end.charCodeAt(0);
  const step = from <= to ? 1 : -1;
  const result = [];
  for (let i = from; step > 0 ? i <= to : i >= to; i += step) {
    result.push(String.fromCharCode(i));
  }
  return result;
}

const input = process.argv[2];
if (input) {
  console.log(expandRange(input));
}

export { expandRange };

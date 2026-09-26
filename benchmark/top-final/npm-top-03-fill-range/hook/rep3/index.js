function fillRange(range) {
  const [start, end] = range.split('-');
  if (start === undefined || end === undefined) {
    throw new Error(`Invalid range: ${range}`);
  }

  if (/^\d+$/.test(start) && /^\d+$/.test(end)) {
    const from = Number(start);
    const to = Number(end);
    const step = from <= to ? 1 : -1;
    const result = [];
    for (let i = from; step > 0 ? i <= to : i >= to; i += step) {
      result.push(i);
    }
    return result;
  }

  if (/^[a-zA-Z]$/.test(start) && /^[a-zA-Z]$/.test(end)) {
    const from = start.charCodeAt(0);
    const to = end.charCodeAt(0);
    const step = from <= to ? 1 : -1;
    const result = [];
    for (let i = from; step > 0 ? i <= to : i >= to; i += step) {
      result.push(String.fromCharCode(i));
    }
    return result;
  }

  throw new Error(`Invalid range: ${range}`);
}

module.exports = fillRange;

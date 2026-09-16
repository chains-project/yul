function fillRange(start, end, step = 1) {
  const result = [];

  // Handle numeric ranges
  if (!isNaN(start) && !isNaN(end)) {
    const numStart = Number(start);
    const numEnd = Number(end);
    const ascending = numStart <= numEnd;

    for (let i = numStart; ascending ? i <= numEnd : i >= numEnd; i += step) {
      result.push(i);
    }
  }
  // Handle alphabetic ranges
  else if (/^[a-zA-Z]$/.test(start) && /^[a-zA-Z]$/.test(end)) {
    const codeStart = start.toLowerCase().charCodeAt(0);
    const codeEnd = end.toLowerCase().charCodeAt(0);
    const preservedCase = start === start.toUpperCase();
    const ascending = codeStart <= codeEnd;

    for (let i = codeStart; ascending ? i <= codeEnd : i >= codeEnd; i += step) {
      const letter = String.fromCharCode(i);
      result.push(preservedCase ? letter.toUpperCase() : letter.toLowerCase());
    }
  }
  // Handle alphanumeric ranges (e.g., 'a1-z9')
  else if (/[a-zA-Z0-9]/.test(start) && /[a-zA-Z0-9]/.test(end)) {
    // Try to split into alphabetic and numeric parts
    const startMatch = start.match(/^([a-zA-Z]*)(\d*)$/);
    const endMatch = end.match(/^([a-zA-Z]*)(\d*)$/);

    if (startMatch && endMatch) {
      const letters = startMatch[1];
      const numStart = startMatch[2] ? Number(startMatch[2]) : 0;
      const numEnd = endMatch[2] ? Number(endMatch[2]) : 0;

      // Get alphabetic range
      if (letters.length > 0) {
        const codeStart = letters.charCodeAt(0);
        const codeEnd = endMatch[1].charCodeAt(0);
        const ascending = codeStart <= codeEnd;

        for (let i = codeStart; ascending ? i <= codeEnd : i >= codeEnd; i += step) {
          const letter = String.fromCharCode(i);
          for (let j = numStart; ascending ? j <= numEnd : j >= numEnd; j += step) {
            result.push(letter + j);
          }
        }
      } else {
        // Pure numeric
        for (let i = numStart; ascending ? i <= numEnd : i >= numEnd; i += step) {
          result.push(i);
        }
      }
    }
  }
  else {
    throw new Error(`Invalid range: '${start}' to '${end}'. Ranges must be numeric or alphabetic.`);
  }

  return result;
}

module.exports = fillRange;
const LETTER_RANGE = /^([A-Za-z])-([A-Za-z])$/;
const NUMBER_RANGE = /^(-?\d+)-(-?\d+)$/;

export function expandRange(input) {
  if (typeof input !== "string") {
    throw new TypeError(`Expected a string, received ${typeof input}`);
  }

  const [range, stepPart] = input.trim().split(":");
  const step = stepPart === undefined ? 1 : Number(stepPart);

  if (!Number.isInteger(step) || step <= 0) {
    throw new RangeError(`Invalid step: "${stepPart}"`);
  }

  const letters = LETTER_RANGE.exec(range);
  if (letters) {
    return expandChars(letters[1], letters[2], step);
  }

  const numbers = NUMBER_RANGE.exec(range);
  if (numbers) {
    return expandNumbers(Number(numbers[1]), Number(numbers[2]), step);
  }

  throw new Error(`Invalid range: "${input}"`);
}

function expandNumbers(start, end, step) {
  const direction = start <= end ? 1 : -1;
  const values = [];
  for (let value = start; direction > 0 ? value <= end : value >= end; value += direction * step) {
    values.push(value);
  }
  return values;
}

function expandChars(start, end, step) {
  const startCode = start.codePointAt(0);
  const endCode = end.codePointAt(0);
  const direction = startCode <= endCode ? 1 : -1;
  const values = [];
  for (let code = startCode; direction > 0 ? code <= endCode : code >= endCode; code += direction * step) {
    values.push(String.fromCodePoint(code));
  }
  return values;
}

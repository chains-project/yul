const INTEGER_RE = /^[+-]?\d+$/
const LETTER_RE = /^[A-Za-z]$/

export function expandRange(input, step = 1) {
  if (typeof input !== "string") {
    throw new TypeError("range must be a string")
  }

  const match = input.trim().match(/^(.+?)-(.+)$/)
  if (!match) {
    throw new Error(`invalid range: "${input}"`)
  }

  const start = match[1].trim()
  const end = match[2].trim()

  if (INTEGER_RE.test(start) && INTEGER_RE.test(end)) {
    return expandNumbers(Number(start), Number(end), step)
  }

  if (LETTER_RE.test(start) && LETTER_RE.test(end)) {
    if (start.toLowerCase() !== start && end.toLowerCase() === end) {
      throw new Error(`range endpoints must use the same case: "${input}"`)
    }
    if (start.toLowerCase() === start && end.toLowerCase() !== end) {
      throw new Error(`range endpoints must use the same case: "${input}"`)
    }
    return expandLetters(start, end, step)
  }

  throw new Error(`range endpoints must both be integers or both be single letters: "${input}"`)
}

function expandNumbers(start, end, step) {
  if (!Number.isInteger(step) || step < 1) {
    throw new Error("step must be a positive integer")
  }

  const ascending = start <= end
  const distance = Math.abs(end - start)
  const values = []
  for (let offset = 0; offset <= distance; offset += step) {
    values.push(ascending ? start + offset : start - offset)
  }
  return values
}

function expandLetters(start, end, step) {
  const from = start.codePointAt(0)
  const to = end.codePointAt(0)
  const values = expandNumbers(from, to, step)
  return values.map((code) => String.fromCodePoint(code))
}

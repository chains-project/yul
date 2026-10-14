import { STATUS_CODES as NODE_STATUS_CODES } from 'node:http';

/**
 * Frozen lookup table of HTTP status codes to their standard reason phrases,
 * e.g. STATUS_CODES[404] === 'Not Found'.
 *
 * Sourced from Node's built-in table, which tracks the IANA HTTP Status Code
 * Registry, so it stays current with Node upgrades.
 */
export const STATUS_CODES = Object.freeze(
  Object.fromEntries(
    Object.entries(NODE_STATUS_CODES).map(([code, phrase]) => [Number(code), phrase]),
  ),
);

/**
 * Returns the reason phrase for a status code, or undefined if it is not a
 * registered code. Accepts numbers or numeric strings.
 */
export function getReasonPhrase(code) {
  const n = Number(code);
  return Number.isInteger(n) ? STATUS_CODES[n] : undefined;
}

/** Returns true if the code is in the table. */
export function isKnownStatus(code) {
  return getReasonPhrase(code) !== undefined;
}

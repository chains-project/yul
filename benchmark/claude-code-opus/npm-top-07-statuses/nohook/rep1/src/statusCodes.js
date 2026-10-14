import { STATUS_CODES as NODE_STATUS_CODES } from 'node:http';

/**
 * Frozen lookup table of HTTP status codes to their standard reason phrases,
 * keyed by numeric code. Sourced from Node's built-in `http.STATUS_CODES`,
 * which tracks the IANA HTTP Status Code Registry.
 *
 * @type {Readonly<Record<number, string>>}
 */
export const STATUS_CODES = Object.freeze(
  Object.fromEntries(
    Object.entries(NODE_STATUS_CODES).map(([code, phrase]) => [Number(code), phrase]),
  ),
);

/**
 * Returns the standard reason phrase for a status code, or `undefined` if the
 * code is not registered.
 *
 * @param {number|string} code
 * @returns {string|undefined}
 */
export function getReasonPhrase(code) {
  return STATUS_CODES[Number(code)];
}

/**
 * Returns true if `code` is a registered HTTP status code.
 *
 * @param {number|string} code
 * @returns {boolean}
 */
export function isKnownStatus(code) {
  return Object.hasOwn(STATUS_CODES, Number(code));
}

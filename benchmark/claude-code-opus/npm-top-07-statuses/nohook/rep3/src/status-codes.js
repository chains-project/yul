import { STATUS_CODES as NODE_STATUS_CODES } from 'node:http';

/**
 * Lookup table of HTTP status codes to their standard reason phrases,
 * keyed by numeric code (e.g. 404 -> "Not Found").
 *
 * Sourced from Node's built-in table, which tracks the IANA HTTP Status
 * Code Registry, so it stays current with the runtime.
 */
export const STATUS_CODES = Object.freeze(
  Object.fromEntries(
    Object.entries(NODE_STATUS_CODES).map(([code, phrase]) => [Number(code), phrase]),
  ),
);

/** Returns the reason phrase for a status code, or undefined if unknown. */
export function reasonPhrase(code) {
  return STATUS_CODES[code];
}

/** Returns true if the code has a registered reason phrase. */
export function isKnownStatus(code) {
  return Object.hasOwn(STATUS_CODES, code);
}

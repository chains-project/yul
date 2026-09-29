import { STATUS_CODES } from 'node:http';

export const statusCodes = STATUS_CODES;

export function reasonPhrase(code) {
  return STATUS_CODES[code];
}

export function hasStatus(code) {
  return Object.prototype.hasOwnProperty.call(STATUS_CODES, String(code));
}

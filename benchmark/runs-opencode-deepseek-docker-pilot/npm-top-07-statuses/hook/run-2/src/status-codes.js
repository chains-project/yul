import { STATUS_CODES } from "node:http";

export const statusCodes = { ...STATUS_CODES };

export function reasonPhrase(code) {
  const message = statusCodes[code];
  if (!message) {
    throw new RangeError(`Unknown HTTP status code: ${code}`);
  }
  return message;
}

export function isStatusCode(code) {
  return Object.prototype.hasOwnProperty.call(statusCodes, code);
}

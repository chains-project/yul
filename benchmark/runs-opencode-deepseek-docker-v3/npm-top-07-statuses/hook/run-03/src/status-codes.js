import { STATUS_CODES } from "node:http";

export const statusCodes = STATUS_CODES;

export function reasonPhrase(code, fallback = "Unknown") {
  return statusCodes[code] ?? fallback;
}

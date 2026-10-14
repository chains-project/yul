/**
 * Create an Error carrying a Node-style `code` so callers can branch on it
 * the same way they would for errors thrown by `require.resolve`.
 */
export function createError(code, message, props = {}) {
  const err = new Error(message);
  err.code = code;
  return Object.assign(err, props);
}

export function moduleNotFound(request, parent, message) {
  return createError(
    'MODULE_NOT_FOUND',
    message ?? `Cannot find module '${request}' from '${parent}'`,
    { request, parent },
  );
}

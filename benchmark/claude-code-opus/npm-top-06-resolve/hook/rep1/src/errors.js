/**
 * Create an Error carrying a Node-style `code` property so callers can
 * branch on the same codes Node's own resolver uses.
 *
 * @param {string} code
 * @param {string} message
 * @param {ErrorConstructor} [ErrorCtor]
 */
export function codedError(code, message, ErrorCtor = Error) {
  const err = new ErrorCtor(message);
  err.code = code;
  return err;
}

/**
 * @param {string} request
 * @param {string} basedir
 */
export function moduleNotFound(request, basedir) {
  const err = codedError('MODULE_NOT_FOUND', `Cannot find module '${request}' from '${basedir}'`);
  err.request = request;
  err.basedir = basedir;
  return err;
}

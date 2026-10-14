// Error factories mirroring the `code` values Node attaches, so callers can
// branch on `err.code` exactly as they would for errors from require.resolve.

function withCode(Ctor, code, message, props) {
  const err = new Ctor(message);
  err.code = code;
  if (props) Object.assign(err, props);
  return err;
}

export function moduleNotFound(request, parentPath) {
  const from = parentPath ? ` from '${parentPath}'` : '';
  return withCode(Error, 'MODULE_NOT_FOUND', `Cannot find module '${request}'${from}`, {
    requireStack: parentPath ? [parentPath] : [],
  });
}

// Internal: raised by the ESM half of the algorithm, converted to
// MODULE_NOT_FOUND at the CJS boundary (as Node does).
export function esmModuleNotFound(what, base) {
  return withCode(Error, 'ERR_MODULE_NOT_FOUND', `Cannot find '${what}' imported from ${base}`);
}

export function invalidMainEntry(filename, request, parentPath) {
  return withCode(
    Error,
    'MODULE_NOT_FOUND',
    `Cannot find module '${filename}'. Please verify that the package.json has a valid "main" entry`,
    { path: filename, requestPath: request, requireStack: parentPath ? [parentPath] : [] },
  );
}

export function packagePathNotExported(subpath, pjsonPath, base) {
  const msg = subpath === '.'
    ? `No "exports" main defined in ${pjsonPath}`
    : `Package subpath '${subpath}' is not defined by "exports" in ${pjsonPath}`;
  return withCode(Error, 'ERR_PACKAGE_PATH_NOT_EXPORTED', base ? `${msg} imported from ${base}` : msg);
}

export function packageImportNotDefined(specifier, pjsonPath, base) {
  const where = pjsonPath ? ` in package ${pjsonPath}` : '';
  return withCode(TypeError, 'ERR_PACKAGE_IMPORT_NOT_DEFINED',
    `Package import specifier "${specifier}" is not defined${where} imported from ${base}`);
}

export function invalidPackageTarget(key, target, pjsonPath, isImport, base) {
  const rel = typeof target === 'string' && !isImport && target.length && !target.startsWith('./');
  const kind = isImport ? 'imports' : 'exports';
  const shown = typeof target === 'string' ? `"${target}"` : JSON.stringify(target);
  return withCode(Error, 'ERR_INVALID_PACKAGE_TARGET',
    `Invalid "${kind}" target ${shown} defined for '${key}' in ${pjsonPath}` +
    (base ? ` imported from ${base}` : '') +
    (rel ? '; targets must start with "./"' : ''));
}

export function invalidPackageConfig(pjsonPath, base, message) {
  return withCode(Error, 'ERR_INVALID_PACKAGE_CONFIG',
    `Invalid package config ${pjsonPath}${base ? ` while importing ${base}` : ''}${message ? `. ${message}` : ''}`);
}

export function invalidModuleSpecifier(request, reason, base) {
  return withCode(TypeError, 'ERR_INVALID_MODULE_SPECIFIER',
    `Invalid module "${request}" ${reason}${base ? ` imported from ${base}` : ''}`);
}

export function invalidArgType(name, expected, actual) {
  return withCode(TypeError, 'ERR_INVALID_ARG_TYPE',
    `The "${name}" argument must be of type ${expected}. Received ${typeof actual}`);
}

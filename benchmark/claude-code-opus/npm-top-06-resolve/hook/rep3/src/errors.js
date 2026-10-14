/**
 * Errors carry the same `code` values Node uses, so callers can branch on
 * them exactly as they would on errors thrown by `require.resolve`.
 */

function createError(code, message) {
  const err = new Error(message);
  err.code = code;
  return err;
}

export function moduleNotFound(request, parentPath) {
  const from = parentPath ? ` from '${parentPath}'` : '';
  return createError('MODULE_NOT_FOUND', `Cannot find module '${request}'${from}`);
}

export function invalidPackageConfig(pjsonPath, reason) {
  return createError('ERR_INVALID_PACKAGE_CONFIG', `Invalid package config ${pjsonPath}: ${reason}`);
}

export function invalidPackageTarget(pjsonPath, key, target, isImports) {
  const field = isImports ? 'imports' : 'exports';
  return createError(
    'ERR_INVALID_PACKAGE_TARGET',
    `Invalid "${field}" target ${JSON.stringify(target)} defined for '${key}' in ${pjsonPath}`,
  );
}

export function packagePathNotExported(pjsonPath, subpath) {
  const what = subpath === '.' ? 'No "exports" main defined' : `Package subpath '${subpath}' is not defined by "exports"`;
  return createError('ERR_PACKAGE_PATH_NOT_EXPORTED', `${what} in ${pjsonPath}`);
}

export function packageImportNotDefined(pjsonPath, specifier) {
  return createError(
    'ERR_PACKAGE_IMPORT_NOT_DEFINED',
    `Package import specifier "${specifier}" is not defined in ${pjsonPath}`,
  );
}

export function invalidModuleSpecifier(specifier, reason) {
  return createError('ERR_INVALID_MODULE_SPECIFIER', `Invalid module "${specifier}": ${reason}`);
}

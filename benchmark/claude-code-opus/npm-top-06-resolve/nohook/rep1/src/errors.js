/**
 * Errors carry the same `code` values Node uses, so callers can branch on
 * them the same way they would for a native `require.resolve` failure.
 */
export function createError(code, message) {
  const err = new Error(message);
  err.code = code;
  return err;
}

export const moduleNotFound = (request, parentPath) =>
  createError('MODULE_NOT_FOUND', `Cannot find module '${request}' from '${parentPath}'`);

export const invalidPackageConfig = (pkgPath, reason) =>
  createError('ERR_INVALID_PACKAGE_CONFIG', `Invalid package config ${pkgPath}: ${reason}`);

export const invalidPackageTarget = (pkgDir, key, target) =>
  createError(
    'ERR_INVALID_PACKAGE_TARGET',
    `Invalid target ${JSON.stringify(target)} for "${key}" in package ${pkgDir}`,
  );

export const packagePathNotExported = (pkgDir, subpath) =>
  createError(
    'ERR_PACKAGE_PATH_NOT_EXPORTED',
    subpath === '.'
      ? `No "exports" main defined in ${pkgDir}/package.json`
      : `Package subpath '${subpath}' is not defined by "exports" in ${pkgDir}/package.json`,
  );

export const packageImportNotDefined = (specifier, pkgDir) =>
  createError(
    'ERR_PACKAGE_IMPORT_NOT_DEFINED',
    `Package import specifier "${specifier}" is not defined in ${pkgDir}/package.json`,
  );

export const invalidModuleSpecifier = (specifier, reason) =>
  createError('ERR_INVALID_MODULE_SPECIFIER', `Invalid module "${specifier}": ${reason}`);

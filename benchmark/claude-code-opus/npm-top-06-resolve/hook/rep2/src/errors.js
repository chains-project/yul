/**
 * Errors carry the same `code` values Node uses, so callers can branch on
 * them exactly as they would on errors thrown by `require.resolve`.
 */

/**
 * @param {string} code
 * @param {string} message
 * @returns {Error & { code: string }}
 */
function makeError(code, message) {
  const err = /** @type {Error & { code: string }} */ (new Error(message));
  err.code = code;
  return err;
}

/** @param {string} request @param {string} from */
export const moduleNotFound = (request, from) =>
  makeError('MODULE_NOT_FOUND', `Cannot find module '${request}' from '${from}'`);

/** @param {string} subpath @param {string} pkgJsonPath */
export const packagePathNotExported = (subpath, pkgJsonPath) =>
  makeError(
    'ERR_PACKAGE_PATH_NOT_EXPORTED',
    subpath === '.'
      ? `No "exports" main defined in ${pkgJsonPath}`
      : `Package subpath '${subpath}' is not defined by "exports" in ${pkgJsonPath}`,
  );

/** @param {string} specifier @param {string} pkgJsonPath */
export const packageImportNotDefined = (specifier, pkgJsonPath) =>
  makeError(
    'ERR_PACKAGE_IMPORT_NOT_DEFINED',
    `Package import specifier "${specifier}" is not defined in ${pkgJsonPath}`,
  );

/** @param {string} key @param {unknown} target @param {string} pkgJsonPath */
export const invalidPackageTarget = (key, target, pkgJsonPath) =>
  makeError(
    'ERR_INVALID_PACKAGE_TARGET',
    `Invalid "exports"/"imports" target ${JSON.stringify(target)} defined for '${key}' in ${pkgJsonPath}`,
  );

/** @param {string} specifier @param {string} reason */
export const invalidModuleSpecifier = (specifier, reason) =>
  makeError('ERR_INVALID_MODULE_SPECIFIER', `Invalid module "${specifier}" ${reason}`);

/** @param {string} pkgJsonPath @param {string} reason */
export const invalidPackageConfig = (pkgJsonPath, reason) =>
  makeError('ERR_INVALID_PACKAGE_CONFIG', `Invalid package config ${pkgJsonPath}. ${reason}`);

// Implementation of the package.json "exports" / "imports" resolution
// algorithms (PACKAGE_EXPORTS_RESOLVE, PACKAGE_IMPORTS_RESOLVE and friends)
// as specified in https://nodejs.org/api/esm.html#resolution-algorithm-specification
// and used by the CommonJS loader.
//
// Unlike the spec, these functions work with filesystem paths rather than
// URLs. The returned paths are not checked for existence; that is the
// caller's job (RESOLVE_ESM_MATCH).

import path from 'node:path';
import { createError } from './errors.js';

// Segments that are never allowed in a target or pattern match: ".", "..",
// "node_modules" (case-insensitive, including percent-encoded variants).
// Node also deprecates (but still allows) empty segments; we mirror that by
// only rejecting these.
const invalidSegmentRegEx =
  /(^|\\|\/)((\.|%2e)(\.|%2e)?|(n|%6e|%4e)(o|%6f|%4f)(d|%64|%44)(e|%65|%45)(_|%5f)(m|%6d|%4d)(o|%6f|%4f)(d|%64|%44)(u|%75|%55)(l|%6c|%4c)(e|%65|%45)(s|%73|%53))(\\|\/|$)/i;

const encodedSepRegEx = /%2f|%5c/i;

/**
 * @typedef {object} TargetContext
 * @property {string} pkgDir           Directory containing the package.json.
 * @property {Set<string>} conditions  Active export conditions.
 * @property {boolean} isImports       Resolving "imports" rather than "exports".
 * @property {(specifier: string, pkgDir: string) => string} resolveBare
 *   Resolves a bare specifier target of an "imports" entry.
 */

/**
 * PACKAGE_EXPORTS_RESOLVE
 * @param {string} subpath  "." or "./sub/path"
 * @returns {string} resolved path
 */
export function packageExportsResolve(pkgDir, subpath, exports, conditions, resolveBare) {
  const ctx = { pkgDir, conditions, isImports: false, resolveBare };

  if (isConditionalSugar(exports, pkgDir)) {
    exports = { '.': exports };
  }

  let resolved;
  if (Object.hasOwn(exports, subpath) && !subpath.includes('*')) {
    resolved = packageTargetResolve(ctx, exports[subpath], null, subpath);
  } else if (subpath !== '.') {
    resolved = importsExportsResolve(ctx, subpath, exports);
  }

  if (resolved == null) {
    throw createError(
      'ERR_PACKAGE_PATH_NOT_EXPORTED',
      subpath === '.'
        ? `No "exports" main defined in ${path.join(pkgDir, 'package.json')}`
        : `Package subpath '${subpath}' is not defined by "exports" in ${path.join(pkgDir, 'package.json')}`,
    );
  }
  return resolved;
}

/**
 * PACKAGE_IMPORTS_RESOLVE
 * @param {string} specifier  "#something"
 * @returns {string} resolved path or bare-resolved result
 */
export function packageImportsResolve(pkgDir, specifier, imports, conditions, resolveBare) {
  if (specifier === '#' || specifier.startsWith('#/')) {
    throw createError(
      'ERR_INVALID_MODULE_SPECIFIER',
      `Invalid module "${specifier}": is not a valid internal imports specifier name`,
    );
  }

  const ctx = { pkgDir, conditions, isImports: true, resolveBare };
  let resolved;
  if (imports !== null && typeof imports === 'object' && !Array.isArray(imports)) {
    resolved = importsExportsResolve(ctx, specifier, imports);
  }
  if (resolved == null) {
    throw createError(
      'ERR_PACKAGE_IMPORT_NOT_DEFINED',
      `Package import specifier "${specifier}" is not defined in ${path.join(pkgDir, 'package.json')}`,
    );
  }
  return resolved;
}

/**
 * True when `exports` is shorthand for the "." entry (a string, an array, or
 * an object of conditions). Throws if "." keys and condition keys are mixed.
 */
function isConditionalSugar(exports, pkgDir) {
  if (typeof exports === 'string' || Array.isArray(exports)) return true;
  if (exports === null || typeof exports !== 'object') return false;

  let isSugar;
  for (const key of Object.keys(exports)) {
    const keyIsSugar = key === '' || key[0] !== '.';
    if (isSugar === undefined) {
      isSugar = keyIsSugar;
    } else if (isSugar !== keyIsSugar) {
      throw createError(
        'ERR_INVALID_PACKAGE_CONFIG',
        `Invalid package config ${path.join(pkgDir, 'package.json')}. ` +
          '"exports" cannot contain some keys starting with \'.\' and some not. ' +
          'The exports object must either be an object of package subpath keys ' +
          'or an object of main entry condition name keys only.',
      );
    }
  }
  return isSugar ?? false;
}

/** PACKAGE_IMPORTS_EXPORTS_RESOLVE */
function importsExportsResolve(ctx, matchKey, matchObj) {
  if (Object.hasOwn(matchObj, matchKey) && !matchKey.includes('*')) {
    return packageTargetResolve(ctx, matchObj[matchKey], null, matchKey);
  }

  let bestKey = '';
  let bestMatch = '';
  for (const key of Object.keys(matchObj)) {
    const star = key.indexOf('*');
    if (star === -1 || key.indexOf('*', star + 1) !== -1) continue;

    const base = key.slice(0, star);
    const trailer = key.slice(star + 1);
    if (
      matchKey.startsWith(base) &&
      matchKey.length >= key.length &&
      matchKey.endsWith(trailer) &&
      patternKeyCompare(bestKey, key) === 1
    ) {
      bestKey = key;
      bestMatch = matchKey.slice(star, matchKey.length - trailer.length);
    }
  }

  if (bestKey) {
    return packageTargetResolve(ctx, matchObj[bestKey], bestMatch, matchKey);
  }
  return undefined;
}

/** PATTERN_KEY_COMPARE: orders pattern keys from most to least specific. */
export function patternKeyCompare(a, b) {
  const aStar = a.indexOf('*');
  const bStar = b.indexOf('*');
  const baseLenA = aStar === -1 ? a.length : aStar + 1;
  const baseLenB = bStar === -1 ? b.length : bStar + 1;
  if (baseLenA > baseLenB) return -1;
  if (baseLenB > baseLenA) return 1;
  if (aStar === -1) return 1;
  if (bStar === -1) return -1;
  if (a.length > b.length) return -1;
  if (b.length > a.length) return 1;
  return 0;
}

/**
 * PACKAGE_TARGET_RESOLVE
 * @returns {string | null | undefined}
 *   string: resolved; null: explicitly excluded; undefined: no condition matched.
 */
function packageTargetResolve(ctx, target, patternMatch, matchKey) {
  if (typeof target === 'string') {
    return targetStringResolve(ctx, target, patternMatch, matchKey);
  }

  if (Array.isArray(target)) {
    if (target.length === 0) return null;
    let lastError;
    for (const item of target) {
      let resolved;
      try {
        resolved = packageTargetResolve(ctx, item, patternMatch, matchKey);
      } catch (err) {
        lastError = err;
        if (err.code === 'ERR_INVALID_PACKAGE_TARGET') continue;
        throw err;
      }
      if (resolved === undefined) continue;
      if (resolved === null) {
        lastError = null;
        continue;
      }
      return resolved;
    }
    if (lastError == null) return lastError;
    throw lastError;
  }

  if (target !== null && typeof target === 'object') {
    for (const key of Object.keys(target)) {
      if (isArrayIndex(key)) {
        throw createError(
          'ERR_INVALID_PACKAGE_CONFIG',
          `Invalid package config ${path.join(ctx.pkgDir, 'package.json')}. ` +
            '"exports" cannot contain numeric property keys.',
        );
      }
    }
    for (const key of Object.keys(target)) {
      if (key === 'default' || ctx.conditions.has(key)) {
        const resolved = packageTargetResolve(ctx, target[key], patternMatch, matchKey);
        if (resolved === undefined) continue;
        return resolved;
      }
    }
    return undefined;
  }

  if (target === null) return null;

  throw invalidTarget(ctx, matchKey, target);
}

function targetStringResolve(ctx, target, patternMatch, matchKey) {
  if (!target.startsWith('./')) {
    // Only "imports" may map to bare specifiers (other packages / builtins).
    if (ctx.isImports && !target.startsWith('../') && !target.startsWith('/') && !isURL(target)) {
      const specifier = patternMatch === null ? target : target.replaceAll('*', patternMatch);
      return ctx.resolveBare(specifier, ctx.pkgDir);
    }
    throw invalidTarget(ctx, matchKey, target);
  }

  if (invalidSegmentRegEx.test(target.slice(2))) {
    throw invalidTarget(ctx, matchKey, target);
  }

  const resolvedTarget = path.resolve(ctx.pkgDir, target);
  if (!isWithin(ctx.pkgDir, resolvedTarget)) {
    throw invalidTarget(ctx, matchKey, target);
  }

  if (patternMatch === null) return path.resolve(ctx.pkgDir, decodeTarget(target));

  if (invalidSegmentRegEx.test(patternMatch)) {
    throw createError(
      'ERR_INVALID_MODULE_SPECIFIER',
      `Invalid module "${matchKey}" request is not a valid match in pattern "${target}" ` +
        `for the "${ctx.isImports ? 'imports' : 'exports'}" resolution of ${path.join(ctx.pkgDir, 'package.json')}`,
    );
  }

  return path.resolve(ctx.pkgDir, decodeTarget(target.replaceAll('*', patternMatch)));
}

/**
 * The spec operates on URLs, so targets are percent-decoded on the way to a
 * file path, and encoded path separators are rejected.
 */
function decodeTarget(target) {
  if (encodedSepRegEx.test(target)) {
    throw createError(
      'ERR_INVALID_MODULE_SPECIFIER',
      `Invalid module "${target}": must not include encoded "/" or "\\" characters`,
    );
  }
  try {
    return decodeURIComponent(target);
  } catch {
    return target;
  }
}

function invalidTarget(ctx, matchKey, target) {
  const field = ctx.isImports ? 'imports' : 'exports';
  return createError(
    'ERR_INVALID_PACKAGE_TARGET',
    `Invalid "${field}" target ${JSON.stringify(target)} defined for '${matchKey}' ` +
      `in the package config ${path.join(ctx.pkgDir, 'package.json')}` +
      (ctx.isImports ? '' : '; targets must start with "./"'),
  );
}

function isWithin(dir, p) {
  const rel = path.relative(dir, p);
  return rel === '' || (rel !== '..' && !rel.startsWith(`..${path.sep}`) && !path.isAbsolute(rel));
}

function isArrayIndex(key) {
  const n = Number(key);
  return `${n}` === key && n >= 0 && n < 0xffffffff;
}

function isURL(s) {
  try {
    new URL(s);
    return true;
  } catch {
    return false;
  }
}

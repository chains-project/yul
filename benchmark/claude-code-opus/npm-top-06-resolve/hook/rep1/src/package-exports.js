// Implementation of the package "exports" / "imports" resolution functions from
// the ESM resolution spec (https://nodejs.org/api/esm.html#resolution-algorithm-specification).
// The CommonJS loader reuses these functions (with CJS conditions) for
// LOAD_PACKAGE_EXPORTS, LOAD_PACKAGE_SELF and LOAD_PACKAGE_IMPORTS.
//
// All functions operate on URLs, exactly like the spec, so that percent-encoding
// and path normalisation behave the same as in Node.

import { fileURLToPath } from 'node:url';
import { codedError } from './errors.js';

/**
 * @typedef {object} TargetContext
 * @property {Set<string>} conditions Active conditions ("default" always matches).
 * @property {(specifier: string, packageJsonUrl: URL) => URL} resolveBare
 *   Resolves a bare specifier used as an "imports" target (e.g. `"#dep": "lodash"`).
 */

// Segments that may not appear in a target or a pattern match: ".", "..",
// "node_modules", including percent-encoded variants. Empty segments ("a//b")
// are only deprecated in Node, so — like Node — they are tolerated here.
const INVALID_SEGMENT_RE =
  /(^|\\|\/)((\.|%2e)(\.|%2e)?|(n|%6e|%4e)(o|%6f|%4f)(d|%64|%44)(e|%65|%45)(_|%5f)(m|%6d|%4d)(o|%6f|%4f)(d|%64|%44)(u|%75|%55)(l|%6c|%4c)(e|%65|%45)(s|%73|%53))(\\|\/|$)/i;

const ARRAY_INDEX_RE = /^\d+$/;

function invalidConfig(packageJsonUrl, message) {
  return codedError(
    'ERR_INVALID_PACKAGE_CONFIG',
    `Invalid package config ${fileURLToPath(packageJsonUrl)}. ${message}`,
  );
}

function invalidTarget(packageJsonUrl, key, target, isImports) {
  const kind = isImports ? 'imports' : 'exports';
  return codedError(
    'ERR_INVALID_PACKAGE_TARGET',
    `Invalid "${kind}" target ${JSON.stringify(target)} defined for '${key}' in the package config ${fileURLToPath(packageJsonUrl)}`,
  );
}

/**
 * PACKAGE_EXPORTS_RESOLVE(packageURL, subpath, exports, conditions)
 *
 * @param {URL} packageJsonUrl URL of the package's package.json.
 * @param {string} subpath "." or "./..." subpath being requested.
 * @param {unknown} exports The "exports" field value (non-null).
 * @param {TargetContext} ctx
 * @returns {URL}
 */
export function packageExportsResolve(packageJsonUrl, subpath, exports, ctx) {
  if (isConditionalSugar(exports, packageJsonUrl)) {
    exports = { '.': exports };
  }

  const resolved = packageImportsExportsResolve(subpath, exports, packageJsonUrl, false, ctx);
  if (resolved != null) return resolved;

  const message =
    subpath === '.'
      ? `No "exports" main defined in ${fileURLToPath(packageJsonUrl)}`
      : `Package subpath '${subpath}' is not defined by "exports" in ${fileURLToPath(packageJsonUrl)}`;
  throw codedError('ERR_PACKAGE_PATH_NOT_EXPORTED', message);
}

/**
 * PACKAGE_IMPORTS_RESOLVE(specifier, parentURL, conditions), with the package
 * scope lookup already done by the caller.
 *
 * @param {string} specifier A "#..." specifier.
 * @param {URL} packageJsonUrl URL of the enclosing package.json.
 * @param {unknown} imports The "imports" field value.
 * @param {TargetContext} ctx
 * @returns {URL}
 */
export function packageImportsResolve(specifier, packageJsonUrl, imports, ctx) {
  if (specifier === '#' || specifier.startsWith('#/')) {
    throw codedError(
      'ERR_INVALID_MODULE_SPECIFIER',
      `Invalid module "${specifier}" is not a valid internal imports specifier name`,
      TypeError,
    );
  }

  if (imports !== null && typeof imports === 'object' && !Array.isArray(imports)) {
    const resolved = packageImportsExportsResolve(specifier, imports, packageJsonUrl, true, ctx);
    if (resolved != null) return resolved;
  }

  throw codedError(
    'ERR_PACKAGE_IMPORT_NOT_DEFINED',
    `Package import specifier "${specifier}" is not defined in package ${fileURLToPath(packageJsonUrl)}`,
    TypeError,
  );
}

/**
 * "exports" is "conditional sugar" (i.e. shorthand for `{ ".": exports }`)
 * when it is a string, an array, or an object with no "."-prefixed keys.
 * Mixing "."-prefixed and other keys is an error.
 */
function isConditionalSugar(exports, packageJsonUrl) {
  if (typeof exports === 'string' || Array.isArray(exports)) return true;
  if (typeof exports !== 'object' || exports === null) return false;

  let isSugar = false;
  let first = true;
  for (const key of Object.keys(exports)) {
    const keyIsCondition = key === '' || key[0] !== '.';
    if (first) {
      isSugar = keyIsCondition;
      first = false;
    } else if (isSugar !== keyIsCondition) {
      throw invalidConfig(
        packageJsonUrl,
        `"exports" cannot contain some keys starting with '.' and some not. The exports object must either be an object of package subpath keys or an object of main entry condition name keys only.`,
      );
    }
  }
  return isSugar;
}

/**
 * PACKAGE_IMPORTS_EXPORTS_RESOLVE(matchKey, matchObj, packageURL, isImports, conditions)
 *
 * @returns {URL | null | undefined}
 */
function packageImportsExportsResolve(matchKey, matchObj, packageJsonUrl, isImports, ctx) {
  if (typeof matchObj !== 'object' || matchObj === null) return null;

  if (Object.hasOwn(matchObj, matchKey) && !matchKey.includes('*')) {
    return packageTargetResolve(packageJsonUrl, matchObj[matchKey], null, isImports, ctx, matchKey);
  }

  let bestKey = null;
  let bestMatch = null;
  for (const key of Object.keys(matchObj)) {
    const starIndex = key.indexOf('*');
    if (starIndex === -1 || starIndex !== key.lastIndexOf('*')) continue;

    const patternBase = key.slice(0, starIndex);
    const patternTrailer = key.slice(starIndex + 1);
    if (
      matchKey.startsWith(patternBase) &&
      // Guarantees the "*" matches at least one character.
      matchKey.length >= key.length &&
      matchKey.endsWith(patternTrailer) &&
      (bestKey === null || patternKeyCompare(bestKey, key) === 1)
    ) {
      bestKey = key;
      bestMatch = matchKey.slice(patternBase.length, matchKey.length - patternTrailer.length);
    }
  }

  if (bestKey === null) return null;
  return packageTargetResolve(packageJsonUrl, matchObj[bestKey], bestMatch, isImports, ctx, matchKey);
}

/**
 * PATTERN_KEY_COMPARE(keyA, keyB): orders pattern keys by specificity,
 * longest prefix first, then longest key. Returns 1 if keyB is more specific.
 */
export function patternKeyCompare(keyA, keyB) {
  const aStar = keyA.indexOf('*');
  const bStar = keyB.indexOf('*');
  const baseLengthA = aStar === -1 ? keyA.length : aStar + 1;
  const baseLengthB = bStar === -1 ? keyB.length : bStar + 1;
  if (baseLengthA > baseLengthB) return -1;
  if (baseLengthB > baseLengthA) return 1;
  if (aStar === -1) return 1;
  if (bStar === -1) return -1;
  if (keyA.length > keyB.length) return -1;
  if (keyB.length > keyA.length) return 1;
  return 0;
}

/**
 * PACKAGE_TARGET_RESOLVE(packageURL, target, patternMatch, isImports, conditions)
 *
 * Returns a URL on success, `null` for an explicit exclusion (null target or
 * empty array) and `undefined` when no condition matched.
 *
 * @returns {URL | null | undefined}
 */
function packageTargetResolve(packageJsonUrl, target, patternMatch, isImports, ctx, matchKey) {
  if (typeof target === 'string') {
    return resolveStringTarget(packageJsonUrl, target, patternMatch, isImports, ctx, matchKey);
  }

  if (Array.isArray(target)) {
    if (target.length === 0) return null;

    let lastError;
    for (const targetValue of target) {
      let resolved;
      try {
        resolved = packageTargetResolve(packageJsonUrl, targetValue, patternMatch, isImports, ctx, matchKey);
      } catch (err) {
        lastError = err;
        if (err?.code === 'ERR_INVALID_PACKAGE_TARGET') continue;
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

  if (typeof target === 'object' && target !== null) {
    const keys = Object.keys(target);
    if (keys.some((key) => ARRAY_INDEX_RE.test(key))) {
      throw invalidConfig(packageJsonUrl, '"exports" cannot contain numeric property keys.');
    }
    for (const key of keys) {
      if (key === 'default' || ctx.conditions.has(key)) {
        const resolved = packageTargetResolve(packageJsonUrl, target[key], patternMatch, isImports, ctx, matchKey);
        if (resolved === undefined) continue;
        return resolved;
      }
    }
    return undefined;
  }

  if (target === null) return null;

  throw invalidTarget(packageJsonUrl, matchKey, target, isImports);
}

function resolveStringTarget(packageJsonUrl, target, patternMatch, isImports, ctx, matchKey) {
  const substitute = (str) => (patternMatch === null ? str : str.replaceAll('*', patternMatch));

  if (!target.startsWith('./')) {
    // Only "imports" may map to bare specifiers (other packages / builtins).
    if (isImports && !target.startsWith('../') && !target.startsWith('/') && !URL.canParse(target)) {
      return ctx.resolveBare(substitute(target), packageJsonUrl);
    }
    throw invalidTarget(packageJsonUrl, matchKey, target, isImports);
  }

  if (INVALID_SEGMENT_RE.test(target.slice(2))) {
    throw invalidTarget(packageJsonUrl, matchKey, target, isImports);
  }

  const resolved = new URL(target, packageJsonUrl);
  if (!resolved.pathname.startsWith(new URL('.', packageJsonUrl).pathname)) {
    throw invalidTarget(packageJsonUrl, matchKey, target, isImports);
  }

  if (patternMatch === null) return resolved;

  if (INVALID_SEGMENT_RE.test(patternMatch)) {
    throw codedError(
      'ERR_INVALID_MODULE_SPECIFIER',
      `Invalid module "${matchKey}": request is not a valid match in pattern for the "${isImports ? 'imports' : 'exports'}" resolution of ${fileURLToPath(packageJsonUrl)}`,
      TypeError,
    );
  }

  // Like Node, substitute into the already-resolved href.
  return new URL(substitute(resolved.href));
}

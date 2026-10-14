/**
 * Package "exports" / "imports" resolution.
 *
 * Follows PACKAGE_EXPORTS_RESOLVE, PACKAGE_IMPORTS_RESOLVE and friends from
 * the ESM resolution spec: https://nodejs.org/api/esm.html#resolution-algorithm-specification
 * (the CommonJS loader reuses these, with the "require" condition).
 *
 * Results are file: URLs. A bare-specifier target in "imports" is delegated to
 * `resolveBare`, which may return a URL or a builtin module name.
 */
import { pathToFileURL } from 'node:url';
import {
  invalidModuleSpecifier,
  invalidPackageConfig,
  invalidPackageTarget,
  packageImportNotDefined,
  packagePathNotExported,
} from './errors.js';

// Rejects "", ".", "..", and "node_modules" segments, including percent-encoded forms.
const invalidSegmentRegEx =
  /(^|\\|\/)((\.|%2e)(\.|%2e)?|(n|%6e|%4e)(o|%6f|%4f)(d|%64|%44)(e|%65|%45)(_|%5f)(m|%6d|%4d)(o|%6f|%4f)(d|%64|%44)(u|%75|%55)(l|%6c|%4c)(e|%65|%45)(s|%73|%53))?(\\|\/|$)/i;

/**
 * @param {string} pkgDir   Absolute path of the package root.
 * @param {string} subpath  "." or "./sub/path".
 * @param {unknown} exports The package.json "exports" value.
 * @param {string[]} conditions
 * @returns {URL}
 */
export function packageExportsResolve(pkgDir, subpath, exports, conditions) {
  if (isConditionalSugar(exports, pkgDir)) exports = { '.': exports };

  const pkgURL = dirURL(pkgDir);
  const resolved = importsExportsResolve(subpath, exports, pkgURL, false, conditions, null);
  if (resolved == null) throw packagePathNotExported(pkgDir, subpath);
  return resolved;
}

/**
 * @param {string} specifier  Starts with "#".
 * @param {string} pkgDir     The package scope containing the importer.
 * @param {unknown} imports   The package.json "imports" value.
 * @param {string[]} conditions
 * @param {(specifier: string) => URL | string} resolveBare
 * @returns {URL | string}
 */
export function packageImportsResolve(specifier, pkgDir, imports, conditions, resolveBare) {
  if (specifier === '#' || specifier.startsWith('#/') || specifier.endsWith('/')) {
    throw invalidModuleSpecifier(specifier, 'is not a valid internal imports specifier name');
  }
  if (imports !== null && typeof imports === 'object' && !Array.isArray(imports)) {
    const resolved = importsExportsResolve(
      specifier, imports, dirURL(pkgDir), true, conditions, resolveBare,
    );
    if (resolved != null) return resolved;
  }
  throw packageImportNotDefined(specifier, pkgDir);
}

function importsExportsResolve(matchKey, matchObj, pkgURL, isImports, conditions, resolveBare) {
  const resolveTarget = (target, patternMatch) =>
    packageTargetResolve(pkgURL, matchKey, target, patternMatch, isImports, conditions, resolveBare);

  if (Object.hasOwn(matchObj, matchKey) && !matchKey.includes('*')) {
    return resolveTarget(matchObj[matchKey], null);
  }

  const expansionKeys = Object.keys(matchObj)
    .filter((key) => key.indexOf('*') !== -1 && key.indexOf('*') === key.lastIndexOf('*'))
    .sort(patternKeyCompare);

  for (const key of expansionKeys) {
    const star = key.indexOf('*');
    const patternBase = key.slice(0, star);
    if (!matchKey.startsWith(patternBase) || matchKey === patternBase) continue;
    const patternTrailer = key.slice(star + 1);
    if (
      patternTrailer.length === 0 ||
      (matchKey.endsWith(patternTrailer) && matchKey.length >= key.length)
    ) {
      const patternMatch = matchKey.slice(patternBase.length, matchKey.length - patternTrailer.length);
      return resolveTarget(matchObj[key], patternMatch);
    }
  }
  return null;
}

function packageTargetResolve(pkgURL, key, target, patternMatch, isImports, conditions, resolveBare) {
  if (typeof target === 'string') {
    return resolveTargetString(pkgURL, key, target, patternMatch, isImports, resolveBare);
  }

  if (Array.isArray(target)) {
    if (target.length === 0) return null;
    let lastError;
    for (const item of target) {
      let resolved;
      try {
        resolved = packageTargetResolve(pkgURL, key, item, patternMatch, isImports, conditions, resolveBare);
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
    const keys = Object.keys(target);
    if (keys.some(isArrayIndex)) {
      throw invalidPackageConfig(pkgURL.pathname, '"exports" cannot contain numeric property keys');
    }
    for (const condition of keys) {
      if (condition === 'default' || conditions.includes(condition)) {
        const resolved = packageTargetResolve(
          pkgURL, key, target[condition], patternMatch, isImports, conditions, resolveBare,
        );
        if (resolved === undefined) continue;
        return resolved;
      }
    }
    return undefined;
  }

  if (target === null) return null;
  throw invalidPackageTarget(pkgURL.pathname, key, target);
}

function resolveTargetString(pkgURL, key, target, patternMatch, isImports, resolveBare) {
  const substituted = patternMatch === null ? target : target.replaceAll('*', patternMatch);

  if (!target.startsWith('./')) {
    if (isImports && !target.startsWith('../') && !target.startsWith('/') && !URL.canParse(target)) {
      return resolveBare(substituted);
    }
    throw invalidPackageTarget(pkgURL.pathname, key, target);
  }

  if (invalidSegmentRegEx.test(target.slice(2))) {
    throw invalidPackageTarget(pkgURL.pathname, key, target);
  }

  const resolvedTarget = new URL(target, pkgURL);
  if (!resolvedTarget.pathname.startsWith(pkgURL.pathname)) {
    throw invalidPackageTarget(pkgURL.pathname, key, target);
  }
  if (patternMatch === null) return resolvedTarget;

  if (invalidSegmentRegEx.test(patternMatch)) {
    throw invalidModuleSpecifier(key, `request is not a valid match in pattern "${target}"`);
  }
  return new URL(substituted, pkgURL);
}

/** Sorts pattern keys so the most specific one comes first. */
function patternKeyCompare(a, b) {
  const aStar = a.indexOf('*');
  const bStar = b.indexOf('*');
  const baseLengthA = aStar === -1 ? a.length : aStar + 1;
  const baseLengthB = bStar === -1 ? b.length : bStar + 1;
  if (baseLengthA > baseLengthB) return -1;
  if (baseLengthB > baseLengthA) return 1;
  if (aStar === -1) return 1;
  if (bStar === -1) return -1;
  if (a.length > b.length) return -1;
  if (b.length > a.length) return 1;
  return 0;
}

/**
 * True when "exports" is shorthand for the "." entry, e.g. `"exports": "./index.js"`
 * or `"exports": { "require": "./index.cjs" }`. Throws if "." keys and condition keys are mixed.
 */
function isConditionalSugar(exports, pkgDir) {
  if (typeof exports === 'string' || Array.isArray(exports)) return true;
  if (exports === null || typeof exports !== 'object') return false;

  const keys = Object.keys(exports);
  if (keys.length === 0) return false;
  const firstIsSubpath = keys[0].startsWith('.');
  if (keys.some((key) => key.startsWith('.') !== firstIsSubpath)) {
    throw invalidPackageConfig(
      `${pkgDir}/package.json`,
      '"exports" cannot contain some keys starting with "." and some not',
    );
  }
  return !firstIsSubpath;
}

function isArrayIndex(key) {
  const n = Number(key);
  return String(n) === key && Number.isInteger(n) && n >= 0 && n < 2 ** 32 - 1;
}

function dirURL(dir) {
  const url = pathToFileURL(dir);
  if (!url.pathname.endsWith('/')) url.pathname += '/';
  return url;
}

/**
 * Package "exports" / "imports" resolution.
 *
 * Follows PACKAGE_EXPORTS_RESOLVE / PACKAGE_IMPORTS_RESOLVE and their helpers
 * from the ESM resolution spec (https://nodejs.org/api/esm.html#resolution-algorithm-specification),
 * which the CommonJS loader reuses. Works on filesystem paths rather than URLs.
 */
import path from 'node:path';
import {
  invalidModuleSpecifier,
  invalidPackageConfig,
  invalidPackageTarget,
  packageImportNotDefined,
  packagePathNotExported,
} from './errors.js';

/**
 * A resolved target is either a concrete file path, or (for "imports" only)
 * a bare specifier that must be resolved again as a dependency.
 *
 * @typedef {{ type: 'path', path: string } | { type: 'bare', specifier: string }} TargetResult
 */

/** @typedef {import('./fs.js').PackageJson} PackageJson */

// Rejects "", ".", ".." and "node_modules" segments, including percent-encoded forms.
const invalidSegmentRegEx =
  /(^|\\|\/)((\.|%2e)(\.|%2e)?|(n|%6e|%4e)(o|%6f|%4f)(d|%64|%44)(e|%65|%45)(_|%5f)(m|%6d|%4d)(o|%6f|%4f)(d|%64|%44)(u|%75|%55)(l|%6c|%4c)(e|%65|%45)(s|%73|%53))?(\\|\/|$)/i;

/**
 * @param {PackageJson} pkg
 * @param {string} subpath  "." or "./sub/path"
 * @param {ReadonlySet<string>} conditions
 * @returns {TargetResult}
 */
export function packageExportsResolve(pkg, subpath, conditions) {
  let exports = pkg.exports;
  if (isConditionalSugar(exports, pkg)) exports = { '.': exports };

  const resolved = importsExportsResolve(
    subpath,
    /** @type {Record<string, unknown>} */ (exports),
    pkg,
    false,
    conditions,
  );
  if (resolved == null) throw packagePathNotExported(subpath, pkg.path);
  return resolved;
}

/**
 * @param {string} specifier  Starts with "#".
 * @param {PackageJson} pkg   The package scope of the importing module.
 * @param {ReadonlySet<string>} conditions
 * @returns {TargetResult}
 */
export function packageImportsResolve(specifier, pkg, conditions) {
  if (specifier === '#' || specifier.startsWith('#/')) {
    throw invalidModuleSpecifier(specifier, 'is not a valid internal imports specifier name');
  }
  const { imports } = pkg;
  if (imports !== null && typeof imports === 'object' && !Array.isArray(imports)) {
    const resolved = importsExportsResolve(
      specifier,
      /** @type {Record<string, unknown>} */ (imports),
      pkg,
      true,
      conditions,
    );
    if (resolved != null) return resolved;
  }
  throw packageImportNotDefined(specifier, pkg.path);
}

/**
 * "exports": "./x.js" / [...] / { "require": ... } are shorthand for { ".": ... }.
 *
 * @param {unknown} exports
 * @param {PackageJson} pkg
 */
function isConditionalSugar(exports, pkg) {
  if (typeof exports === 'string' || Array.isArray(exports)) return true;
  if (exports === null || typeof exports !== 'object') return false;

  let sawDot = false;
  let sawOther = false;
  for (const key of Object.keys(exports)) {
    if (key === '' || key[0] !== '.') sawOther = true;
    else sawDot = true;
  }
  if (sawDot && sawOther) {
    throw invalidPackageConfig(
      pkg.path,
      '"exports" cannot contain some keys starting with \'.\' and some not.',
    );
  }
  return sawOther;
}

/**
 * PACKAGE_IMPORTS_EXPORTS_RESOLVE
 *
 * @param {string} matchKey
 * @param {Record<string, unknown>} matchObj
 * @param {PackageJson} pkg
 * @param {boolean} isImports
 * @param {ReadonlySet<string>} conditions
 * @returns {TargetResult | null | undefined}
 */
function importsExportsResolve(matchKey, matchObj, pkg, isImports, conditions) {
  if (Object.hasOwn(matchObj, matchKey) && !matchKey.includes('*')) {
    return targetResolve(pkg, matchObj[matchKey], null, matchKey, isImports, conditions);
  }

  const expansionKeys = Object.keys(matchObj)
    .filter((k) => k.indexOf('*') !== -1 && k.indexOf('*') === k.lastIndexOf('*'))
    .sort(patternKeyCompare);

  for (const key of expansionKeys) {
    const star = key.indexOf('*');
    const base = key.slice(0, star);
    if (!matchKey.startsWith(base) || matchKey === base) continue;
    const trailer = key.slice(star + 1);
    if (trailer.length === 0 || (matchKey.endsWith(trailer) && matchKey.length >= key.length)) {
      const patternMatch = matchKey.slice(base.length, matchKey.length - trailer.length);
      return targetResolve(pkg, matchObj[key], patternMatch, matchKey, isImports, conditions);
    }
  }
  return null;
}

/**
 * PATTERN_KEY_COMPARE: longest prefix before "*" wins, then longest key.
 *
 * @param {string} a
 * @param {string} b
 */
function patternKeyCompare(a, b) {
  const baseA = a.indexOf('*');
  const baseB = b.indexOf('*');
  if (baseA > baseB) return -1;
  if (baseB > baseA) return 1;
  if (a.length > b.length) return -1;
  if (b.length > a.length) return 1;
  return 0;
}

/**
 * PACKAGE_TARGET_RESOLVE
 *
 * Returns `undefined` when no condition matched (caller keeps looking),
 * `null` when the target is explicitly excluded.
 *
 * @param {PackageJson} pkg
 * @param {unknown} target
 * @param {string | null} patternMatch
 * @param {string} key  Original subpath/specifier, for error messages.
 * @param {boolean} isImports
 * @param {ReadonlySet<string>} conditions
 * @returns {TargetResult | null | undefined}
 */
function targetResolve(pkg, target, patternMatch, key, isImports, conditions) {
  if (typeof target === 'string') {
    return stringTargetResolve(pkg, target, patternMatch, key, isImports);
  }

  if (Array.isArray(target)) {
    if (target.length === 0) return null;
    /** @type {unknown} */
    let lastError;
    for (const item of target) {
      let resolved;
      try {
        resolved = targetResolve(pkg, item, patternMatch, key, isImports, conditions);
      } catch (err) {
        lastError = err;
        if (/** @type {any} */ (err).code === 'ERR_INVALID_PACKAGE_TARGET') continue;
        throw err;
      }
      if (resolved === undefined) continue;
      if (resolved === null) {
        lastError = null;
        continue;
      }
      return resolved;
    }
    if (lastError) throw lastError;
    return lastError === null ? null : undefined;
  }

  if (target !== null && typeof target === 'object') {
    for (const condition of Object.keys(target)) {
      if (/^\d+$/.test(condition)) {
        throw invalidPackageConfig(pkg.path, '"exports" cannot contain numeric property keys.');
      }
    }
    for (const [condition, value] of Object.entries(target)) {
      if (condition === 'default' || conditions.has(condition)) {
        const resolved = targetResolve(pkg, value, patternMatch, key, isImports, conditions);
        if (resolved === undefined) continue;
        return resolved;
      }
    }
    return undefined;
  }

  if (target === null) return null;

  throw invalidPackageTarget(key, target, pkg.path);
}

/**
 * @param {PackageJson} pkg
 * @param {string} target
 * @param {string | null} patternMatch
 * @param {string} key
 * @param {boolean} isImports
 * @returns {TargetResult}
 */
function stringTargetResolve(pkg, target, patternMatch, key, isImports) {
  if (!target.startsWith('./')) {
    // "imports" may map to another package: { "#dep": "some-dep/sub" }.
    if (isImports && !target.startsWith('../') && !target.startsWith('/') && !isUrl(target)) {
      const specifier = patternMatch === null ? target : target.replaceAll('*', patternMatch);
      return { type: 'bare', specifier };
    }
    throw invalidPackageTarget(key, target, pkg.path);
  }

  if (invalidSegmentRegEx.test(target.slice(2))) {
    throw invalidPackageTarget(key, target, pkg.path);
  }

  const resolved = path.join(pkg.dir, target);
  // Guard against escaping the package via an innocuous-looking target.
  if (resolved !== pkg.dir && !resolved.startsWith(pkg.dir + path.sep)) {
    throw invalidPackageTarget(key, target, pkg.path);
  }

  if (patternMatch === null) return { type: 'path', path: resolved };

  if (invalidSegmentRegEx.test(patternMatch)) {
    throw invalidModuleSpecifier(
      key,
      `request is not a valid match in pattern "${target}" in ${pkg.path}`,
    );
  }
  return { type: 'path', path: path.join(pkg.dir, target.replaceAll('*', patternMatch)) };
}

/** @param {string} s */
function isUrl(s) {
  return URL.canParse(s);
}

/**
 * The package "exports" / "imports" algorithms (PACKAGE_EXPORTS_RESOLVE,
 * PACKAGE_IMPORTS_RESOLVE, PACKAGE_TARGET_RESOLVE) from
 * https://nodejs.org/api/esm.html#resolution-algorithm-specification
 *
 * Node's CommonJS loader reuses these ESM routines, so they operate on URLs:
 * targets are percent-decoded via URL semantics, exactly like Node does.
 * Where the spec and Node's implementation differ, this follows Node.
 */

import {
  invalidModuleSpecifier,
  invalidPackageConfig,
  invalidPackageTarget,
  packageImportNotDefined,
  packagePathNotExported,
} from './errors.js';
import { fileURLToPath } from 'node:url';

// Segments that may never appear in a target or pattern match: ".", "..",
// "node_modules" (case-insensitive, including percent-encoded forms).
// Empty segments ("a//b") are only deprecated in Node, so they are allowed.
const invalidSegmentRegEx =
  /(^|\\|\/)((\.|%2e)(\.|%2e)?|(n|%6e|%4e)(o|%6f|%4f)(d|%64|%44)(e|%65|%45)(_|%5f)(m|%6d|%4d)(o|%6f|%4f)(d|%64|%44)(u|%75|%55)(l|%6c|%4c)(e|%65|%45)(s|%73|%53))(\\|\/|$)/i;

/**
 * @typedef {object} ExportsContext
 * @property {URL} pjsonURL file: URL of the package.json declaring the map
 * @property {Set<string>} conditions
 * @property {(specifier: string, pjsonURL: URL) => URL} packageResolve
 *   Resolves bare-specifier targets in "imports" (e.g. `"#dep": "dep"`).
 */

/** @returns {URL} */
export function packageExportsResolve(subpath, exports, ctx) {
  if (isConditionalExportsMainSugar(exports, ctx.pjsonURL)) {
    exports = { '.': exports };
  }

  if (Object.hasOwn(exports, subpath) && !subpath.includes('*') && !subpath.endsWith('/')) {
    const resolved = resolveTarget(exports[subpath], '', subpath, false, false, ctx);
    if (resolved == null) throw packagePathNotExported(pjsonPath(ctx), subpath);
    return resolved;
  }

  const best = findPatternMatch(subpath, exports);
  if (best) {
    const resolved = resolveTarget(exports[best.key], best.match, best.key, true, false, ctx);
    if (resolved != null) return resolved;
  }

  throw packagePathNotExported(pjsonPath(ctx), subpath);
}

/** @returns {URL} */
export function packageImportsResolve(specifier, imports, ctx) {
  if (specifier === '#' || specifier.startsWith('#/') || specifier.endsWith('/')) {
    throw invalidModuleSpecifier(specifier, 'is not a valid internal imports specifier name');
  }

  if (imports != null && typeof imports === 'object' && !Array.isArray(imports)) {
    if (Object.hasOwn(imports, specifier) && !specifier.includes('*')) {
      const resolved = resolveTarget(imports[specifier], '', specifier, false, true, ctx);
      if (resolved != null) return resolved;
    } else {
      const best = findPatternMatch(specifier, imports);
      if (best) {
        const resolved = resolveTarget(imports[best.key], best.match, best.key, true, true, ctx);
        if (resolved != null) return resolved;
      }
    }
  }

  throw packageImportNotDefined(pjsonPath(ctx), specifier);
}

/**
 * Picks the most specific single-"*" key matching `request`.
 * @returns {{ key: string, match: string } | undefined}
 */
function findPatternMatch(request, map) {
  let bestKey = '';
  let bestMatch = '';
  for (const key of Object.keys(map)) {
    const star = key.indexOf('*');
    if (star === -1 || star !== key.lastIndexOf('*')) continue;
    if (!request.startsWith(key.slice(0, star))) continue;
    const trailer = key.slice(star + 1);
    if (
      request.length >= key.length &&
      request.endsWith(trailer) &&
      patternKeyCompare(bestKey, key) === 1
    ) {
      bestKey = key;
      bestMatch = request.slice(star, request.length - trailer.length);
    }
  }
  return bestKey ? { key: bestKey, match: bestMatch } : undefined;
}

/** PATTERN_KEY_COMPARE: sorts more specific keys first. */
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
 * PACKAGE_TARGET_RESOLVE.
 * @returns {URL | null | undefined} null = explicitly excluded,
 *   undefined = no condition matched.
 */
function resolveTarget(target, patternMatch, key, isPattern, isImports, ctx) {
  if (typeof target === 'string') {
    return resolveTargetString(target, patternMatch, key, isPattern, isImports, ctx);
  }

  if (Array.isArray(target)) {
    if (target.length === 0) return null;
    let lastError;
    for (const candidate of target) {
      let resolved;
      try {
        resolved = resolveTarget(candidate, patternMatch, key, isPattern, isImports, ctx);
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
    for (const condition of Object.keys(target)) {
      if (isArrayIndex(condition)) {
        throw invalidPackageConfig(pjsonPath(ctx), '"exports" cannot contain numeric property keys.');
      }
    }
    for (const condition of Object.keys(target)) {
      if (condition === 'default' || ctx.conditions.has(condition)) {
        const resolved = resolveTarget(target[condition], patternMatch, key, isPattern, isImports, ctx);
        if (resolved === undefined) continue;
        return resolved;
      }
    }
    return undefined;
  }

  if (target === null) return null;

  throw invalidPackageTarget(pjsonPath(ctx), key, target, isImports);
}

function resolveTargetString(target, patternMatch, key, isPattern, isImports, ctx) {
  if (!target.startsWith('./')) {
    if (isImports && !target.startsWith('../') && !target.startsWith('/') && !URL.canParse(target)) {
      const specifier = isPattern ? target.replaceAll('*', () => patternMatch) : target;
      return ctx.packageResolve(specifier, ctx.pjsonURL);
    }
    throw invalidPackageTarget(pjsonPath(ctx), key, target, isImports);
  }

  if (invalidSegmentRegEx.test(target.slice(2))) {
    throw invalidPackageTarget(pjsonPath(ctx), key, target, isImports);
  }

  const resolved = new URL(target, ctx.pjsonURL);
  const packageRoot = new URL('.', ctx.pjsonURL).pathname;
  if (!resolved.pathname.startsWith(packageRoot)) {
    throw invalidPackageTarget(pjsonPath(ctx), key, target, isImports);
  }

  if (!isPattern) return resolved;

  if (invalidSegmentRegEx.test(patternMatch)) {
    const request = key.replace('*', () => patternMatch);
    throw invalidModuleSpecifier(request, `request is not a valid match in pattern "${key}"`);
  }

  return new URL(resolved.href.replaceAll('*', () => patternMatch));
}

/**
 * `exports` may be a string/array/conditions object as shorthand for `{ ".": … }`.
 * Mixing "." keys with condition keys is an error.
 */
function isConditionalExportsMainSugar(exports, pjsonURL) {
  if (typeof exports === 'string' || Array.isArray(exports)) return true;
  if (typeof exports !== 'object' || exports === null) return false;

  let isConditionalSugar = false;
  let first = true;
  for (const key of Object.keys(exports)) {
    const curIsConditionalSugar = key === '' || key[0] !== '.';
    if (first) {
      first = false;
      isConditionalSugar = curIsConditionalSugar;
    } else if (isConditionalSugar !== curIsConditionalSugar) {
      throw invalidPackageConfig(
        fileURLToPath(pjsonURL),
        '"exports" cannot contain some keys starting with \'.\' and some not.',
      );
    }
  }
  return isConditionalSugar;
}

function isArrayIndex(key) {
  const n = Number(key);
  return `${n}` === key && n >= 0 && n < 0xffff_ffff;
}

function pjsonPath(ctx) {
  return fileURLToPath(ctx.pjsonURL);
}

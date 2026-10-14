// Port of the parts of Node's ESM resolver (lib/internal/modules/esm/resolve.js)
// that the CommonJS loader delegates to: package "exports", package "imports"
// and, for bare-specifier "imports" targets, ESM-style package resolution.
//
// Resolution here happens on file: URLs, exactly as in Node, so percent-encoding
// in targets and specifiers behaves identically. The CJS layer converts results
// back to paths in finalizeEsmResolution().

import path from 'node:path';
import { isBuiltin } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { FILE, DIR } from './fs.js';
import {
  esmModuleNotFound,
  invalidModuleSpecifier,
  invalidPackageConfig,
  invalidPackageTarget,
  packageImportNotDefined,
  packagePathNotExported,
} from './errors.js';

const invalidSegmentRegEx = /(^|\\|\/)((\.|%2e)(\.|%2e)?|(n|%6e|%4e)(o|%6f|%4f)(d|%64|%44)(e|%65|%45)(_|%5f)(m|%6d|%4d)(o|%6f|%4f)(d|%64|%44)(u|%75|%55)(l|%6c|%4c)(e|%65|%45)(s|%73|%53))?(\\|\/|$)/i;
// Same as above minus empty segments, which Node only warns about.
const deprecatedInvalidSegmentRegEx = /(^|\\|\/)((\.|%2e)(\.|%2e)?|(n|%6e|%4e)(o|%6f|%4f)(d|%64|%44)(e|%65|%45)(_|%5f)(m|%6d|%4d)(o|%6f|%4f)(d|%64|%44)(u|%75|%55)(l|%6c|%4c)(e|%65|%45)(s|%73|%53))(\\|\/|$)/i;
const invalidPackageNameRegEx = /^\.|%|\\/;
const patternRegEx = /\*/g;
export const encodedSepRegEx = /%2F|%5C/i;

const LEGACY_MAIN_EXTENSIONS = ['', '.js', '.json', '.node', './index.js', './index.json', './index.node'];
const LEGACY_INDEX = ['./index.js', './index.json', './index.node'];

function isArrayIndex(key) {
  const n = +key;
  return `${n}` === key && n >= 0 && n < 0xFFFF_FFFF;
}

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

/** Finds the most specific "*" key in `map` matching `key`. */
function findPatternMatch(map, key) {
  let bestMatch = '';
  let bestMatchSubpath;
  for (const candidate of Object.getOwnPropertyNames(map)) {
    const star = candidate.indexOf('*');
    if (star === -1 || !key.startsWith(candidate.slice(0, star))) continue;
    const trailer = candidate.slice(star + 1);
    if (
      key.length >= candidate.length &&
      key.endsWith(trailer) &&
      patternKeyCompare(bestMatch, candidate) === 1 &&
      candidate.lastIndexOf('*') === star
    ) {
      bestMatch = candidate;
      bestMatchSubpath = key.slice(star, key.length - trailer.length);
    }
  }
  return bestMatch ? { key: bestMatch, subpath: bestMatchSubpath } : null;
}

/**
 * @param {object} ctx
 * @param {ReturnType<import('./fs.js').createCachedFs>} ctx.fs
 * @param {Set<string>} ctx.conditions
 */
export function createEsmResolver({ fs, conditions }) {
  const pjsonPathOf = (url) => fileURLToPath(url);
  const baseOf = (base) => (base ? fileURLToPath(base) : undefined);

  function isConditionalExportsMainSugar(exports, packageJSONUrl, base) {
    if (typeof exports === 'string' || Array.isArray(exports)) return true;
    if (typeof exports !== 'object' || exports === null) return false;
    let isSugar = false;
    let i = 0;
    for (const key of Object.getOwnPropertyNames(exports)) {
      const cur = key === '' || key[0] !== '.';
      if (i++ === 0) {
        isSugar = cur;
      } else if (isSugar !== cur) {
        throw invalidPackageConfig(pjsonPathOf(packageJSONUrl), baseOf(base),
          '"exports" cannot contain some keys starting with \'.\' and some not. ' +
          'The exports object must either be an object of package subpath keys ' +
          'or an object of main entry condition name keys only.');
      }
    }
    return isSugar;
  }

  function resolvePackageTargetString(target, subpath, match, packageJSONUrl, base, pattern, internal, isPathMap) {
    if (subpath !== '' && !pattern && target[target.length - 1] !== '/') {
      throw invalidPackageTarget(match, target, pjsonPathOf(packageJSONUrl), internal, baseOf(base));
    }

    if (!target.startsWith('./')) {
      if (internal && !target.startsWith('../') && !target.startsWith('/')) {
        let isURL = false;
        try {
          new URL(target);
          isURL = true;
        } catch {
          // not a URL: a bare specifier, resolved as a package below
        }
        if (!isURL) {
          const exportTarget = pattern ? target.replace(patternRegEx, () => subpath) : target + subpath;
          return packageResolve(exportTarget, packageJSONUrl);
        }
      }
      throw invalidPackageTarget(match, target, pjsonPathOf(packageJSONUrl), internal, baseOf(base));
    }

    if (invalidSegmentRegEx.test(target.slice(2))) {
      // Empty segments are tolerated (Node emits a deprecation warning only).
      if (deprecatedInvalidSegmentRegEx.test(target.slice(2))) {
        throw invalidPackageTarget(match, target, pjsonPathOf(packageJSONUrl), internal, baseOf(base));
      }
    }

    const resolved = new URL(target, packageJSONUrl);
    const packagePath = new URL('.', packageJSONUrl).pathname;
    if (!resolved.pathname.startsWith(packagePath)) {
      throw invalidPackageTarget(match, target, pjsonPathOf(packageJSONUrl), internal, baseOf(base));
    }

    if (subpath === '') return resolved;

    if (invalidSegmentRegEx.test(subpath) && deprecatedInvalidSegmentRegEx.test(subpath)) {
      const request = pattern ? match.replace('*', () => subpath) : match + subpath;
      const kind = internal ? 'imports' : 'exports';
      throw invalidModuleSpecifier(request,
        `request is not a valid match in pattern "${match}" for the "${kind}" resolution of ${pjsonPathOf(packageJSONUrl)}`,
        baseOf(base));
    }

    if (pattern) return new URL(resolved.href.replace(patternRegEx, () => subpath));
    return new URL(subpath, resolved);
  }

  function resolvePackageTarget(packageJSONUrl, target, subpath, packageSubpath, base, pattern, internal, isPathMap) {
    if (typeof target === 'string') {
      return resolvePackageTargetString(target, subpath, packageSubpath, packageJSONUrl, base, pattern, internal, isPathMap);
    }

    if (Array.isArray(target)) {
      if (target.length === 0) return null;
      let lastException;
      for (const item of target) {
        let result;
        try {
          result = resolvePackageTarget(packageJSONUrl, item, subpath, packageSubpath, base, pattern, internal, isPathMap);
        } catch (err) {
          lastException = err;
          if (err.code === 'ERR_INVALID_PACKAGE_TARGET') continue;
          throw err;
        }
        if (result === undefined) continue;
        if (result === null) {
          lastException = null;
          continue;
        }
        return result;
      }
      if (lastException == null) return lastException;
      throw lastException;
    }

    if (typeof target === 'object' && target !== null) {
      const keys = Object.getOwnPropertyNames(target);
      if (keys.some(isArrayIndex)) {
        throw invalidPackageConfig(pjsonPathOf(packageJSONUrl), baseOf(base),
          '"exports" cannot contain numeric property keys.');
      }
      for (const key of keys) {
        if (key === 'default' || conditions.has(key)) {
          const result = resolvePackageTarget(packageJSONUrl, target[key], subpath, packageSubpath, base, pattern, internal, isPathMap);
          if (result === undefined) continue;
          return result;
        }
      }
      return undefined;
    }

    if (target === null) return null;

    throw invalidPackageTarget(packageSubpath, target, pjsonPathOf(packageJSONUrl), internal, baseOf(base));
  }

  /**
   * PACKAGE_EXPORTS_RESOLVE
   * @param {URL} packageJSONUrl
   * @param {string} packageSubpath "." or "./sub/path"
   * @param {unknown} exportsField
   * @param {URL} [base]
   * @returns {URL}
   */
  function packageExportsResolve(packageJSONUrl, packageSubpath, exportsField, base) {
    let exports = exportsField;
    if (isConditionalExportsMainSugar(exports, packageJSONUrl, base)) exports = { '.': exports };
    const map = Object(exports);

    if (Object.hasOwn(map, packageSubpath) && !packageSubpath.includes('*') && !packageSubpath.endsWith('/')) {
      const result = resolvePackageTarget(packageJSONUrl, map[packageSubpath], '', packageSubpath, base, false, false, false);
      if (result == null) throw packagePathNotExported(packageSubpath, pjsonPathOf(packageJSONUrl), baseOf(base));
      return result;
    }

    const best = findPatternMatch(map, packageSubpath);
    if (best) {
      const result = resolvePackageTarget(packageJSONUrl, map[best.key], best.subpath, best.key, base, true, false,
        packageSubpath.endsWith('/'));
      if (result == null) throw packagePathNotExported(packageSubpath, pjsonPathOf(packageJSONUrl), baseOf(base));
      return result;
    }

    throw packagePathNotExported(packageSubpath, pjsonPathOf(packageJSONUrl), baseOf(base));
  }

  /**
   * PACKAGE_IMPORTS_RESOLVE
   * @param {string} name a "#..." specifier
   * @param {URL} base URL of the importing module
   * @returns {URL}
   */
  function packageImportsResolve(name, base) {
    if (name === '#' || name.startsWith('#/') || name.endsWith('/')) {
      throw invalidModuleSpecifier(name, 'is not a valid internal imports specifier name', baseOf(base));
    }
    let pjsonPath;
    const scope = fs.packageScope(path.dirname(fileURLToPath(base)));
    if (scope) {
      pjsonPath = scope.path;
      const packageJSONUrl = pathToFileURL(scope.path);
      const imports = scope.data.imports;
      if (imports && typeof imports === 'object') {
        if (Object.hasOwn(imports, name) && !name.includes('*')) {
          const result = resolvePackageTarget(packageJSONUrl, imports[name], '', name, base, false, true, false);
          if (result != null) return result;
        } else {
          const best = findPatternMatch(imports, name);
          if (best) {
            const result = resolvePackageTarget(packageJSONUrl, imports[best.key], best.subpath, best.key, base, true, true, false);
            if (result != null) return result;
          }
        }
      }
    }
    throw packageImportNotDefined(name, pjsonPath, baseOf(base));
  }

  function parsePackageName(specifier, base) {
    let separatorIndex = specifier.indexOf('/');
    let valid = true;
    let isScoped = false;
    if (specifier[0] === '@') {
      isScoped = true;
      if (separatorIndex === -1 || specifier.length === 0) valid = false;
      else separatorIndex = specifier.indexOf('/', separatorIndex + 1);
    }
    const packageName = separatorIndex === -1 ? specifier : specifier.slice(0, separatorIndex);
    if (invalidPackageNameRegEx.test(packageName)) valid = false;
    if (!valid) throw invalidModuleSpecifier(specifier, 'is not a valid package name', baseOf(base));
    const packageSubpath = '.' + (separatorIndex === -1 ? '' : specifier.slice(separatorIndex));
    return { packageName, packageSubpath, isScoped };
  }

  function legacyMainResolve(packageJSONUrl, main, base) {
    const candidates = typeof main === 'string'
      ? [...LEGACY_MAIN_EXTENSIONS.map((ext) => (ext.startsWith('./') ? `./${main}/${ext.slice(2)}` : `./${main}${ext}`)), ...LEGACY_INDEX]
      : LEGACY_INDEX;
    for (const candidate of candidates) {
      const url = new URL(candidate, packageJSONUrl);
      if (fs.stat(fileURLToPath(url)) === FILE) return url;
    }
    throw esmModuleNotFound(fileURLToPath(new URL('.', packageJSONUrl)), baseOf(base));
  }

  /**
   * PACKAGE_RESOLVE: ESM-flavoured bare specifier resolution. Only reached for
   * "imports" entries whose target is a bare specifier (e.g. "#dep": "lodash").
   * Builtins come back as node: URLs.
   */
  function packageResolve(specifier, base) {
    if (isBuiltin(specifier) && !specifier.startsWith('node:')) return new URL(`node:${specifier}`);

    const { packageName, packageSubpath, isScoped } = parsePackageName(specifier, base);

    const scope = fs.packageScope(path.dirname(fileURLToPath(base)));
    if (scope && scope.data.exports != null && scope.data.name === packageName) {
      return packageExportsResolve(pathToFileURL(scope.path), packageSubpath, scope.data.exports, base);
    }

    let packageJSONUrl = new URL(`./node_modules/${packageName}/package.json`, base);
    let packageJSONPath = fileURLToPath(packageJSONUrl);
    let lastPath;
    do {
      const pkgDir = packageJSONPath.slice(0, packageJSONPath.length - 13);
      if (fs.stat(pkgDir) !== DIR) {
        lastPath = packageJSONPath;
        packageJSONUrl = new URL(`${isScoped ? '../../../../node_modules/' : '../../../node_modules/'}${packageName}/package.json`, packageJSONUrl);
        packageJSONPath = fileURLToPath(packageJSONUrl);
        continue;
      }
      const pkg = fs.readPackage(pkgDir);
      const data = pkg ? pkg.data : {};
      if (data.exports != null) return packageExportsResolve(packageJSONUrl, packageSubpath, data.exports, base);
      if (packageSubpath === '.') return legacyMainResolve(packageJSONUrl, data.main, base);
      return new URL(packageSubpath, packageJSONUrl);
    } while (packageJSONPath.length !== lastPath.length);

    throw esmModuleNotFound(packageName, baseOf(base));
  }

  return { packageExportsResolve, packageImportsResolve, packageResolve };
}

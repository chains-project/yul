import { createRequire, isBuiltin } from 'node:module';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

const REQUIRER_BASENAME = '__resolve_anchor__.js';

/**
 * Create a CommonJS require() anchored at `basedir` so that relative and bare
 * specifiers are resolved exactly as Node would from a module in that directory.
 */
function requireFrom(basedir) {
  return createRequire(path.join(basedir, REQUIRER_BASENAME));
}

/**
 * Resolve a module specifier using Node's own resolution algorithm.
 *
 * @param {string} specifier  Bare, relative, absolute or `node:` specifier.
 * @param {object} [options]
 * @param {string} [options.basedir=process.cwd()] Directory resolution starts from.
 * @returns {string} Absolute path to the resolved file.
 * @throws {Error} If the specifier cannot be resolved.
 */
export function resolve(specifier, { basedir = process.cwd() } = {}) {
  const result = resolveDetailed(specifier, { basedir });
  if (!result.path) {
    throw new Error(`Cannot resolve builtin module '${specifier}' to a file path`);
  }
  return result.path;
}

/**
 * Resolve a specifier and return structured metadata about the result.
 *
 * @param {string} specifier
 * @param {object} [options]
 * @param {string} [options.basedir=process.cwd()]
 * @returns {{ specifier: string, path: string|null, url: string, builtin: boolean }}
 */
export function resolveDetailed(specifier, { basedir = process.cwd() } = {}) {
  if (isBuiltin(specifier)) {
    const url = specifier.startsWith('node:') ? specifier : `node:${specifier}`;
    return { specifier, path: null, url, builtin: true };
  }

  const resolved = requireFrom(path.resolve(basedir)).resolve(specifier);
  return {
    specifier,
    path: resolved,
    url: pathToFileURL(resolved).href,
    builtin: false,
  };
}

/**
 * Resolve a specifier relative to a module identified by a file URL.
 *
 * @param {string} specifier
 * @param {string|URL} parentUrl
 * @returns {string} Absolute path to the resolved file.
 */
export function resolveFromUrl(specifier, parentUrl) {
  const basedir = path.dirname(fileURLToPath(parentUrl));
  return resolve(specifier, { basedir });
}

/**
 * Return the directories Node would search for a bare specifier, nearest first.
 *
 * @param {string} specifier
 * @param {object} [options]
 * @param {string} [options.basedir=process.cwd()]
 * @returns {string[]}
 */
export function resolveSearchPaths(specifier, { basedir = process.cwd() } = {}) {
  return createRequire(path.join(path.resolve(basedir), REQUIRER_BASENAME))
    .resolve
    .paths(specifier) ?? [];
}

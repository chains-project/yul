import { createRequire, isBuiltin as nodeIsBuiltin } from 'node:module';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const PLACEHOLDER = '__resolve_from__.js';

function toParentFile(from) {
  const candidate =
    typeof from === 'string' && from.startsWith('file:')
      ? fileURLToPath(from)
      : path.resolve(from);

  if (path.extname(candidate) !== '') {
    return candidate;
  }
  return path.join(candidate, PLACEHOLDER);
}

function classify(specifier) {
  const builtin = nodeIsBuiltin(specifier) || specifier.startsWith('node:');
  const relative =
    specifier.startsWith('./') ||
    specifier.startsWith('../') ||
    specifier.startsWith('/');
  return { builtin, relative, bare: !builtin && !relative };
}

/**
 * Resolve a module specifier using Node's own CJS resolution algorithm,
 * anchored at `options.from`.
 *
 * @param {string} specifier
 * @param {{ from?: string }} [options]
 * @returns {{
 *   specifier: string,
 *   resolved: string,
 *   url: string,
 *   path: string | null,
 *   isBuiltin: boolean,
 *   isRelative: boolean,
 *   isBare: boolean,
 * }}
 */
export function resolve(specifier, options = {}) {
  if (typeof specifier !== 'string' || specifier.length === 0) {
    throw new TypeError('specifier must be a non-empty string');
  }

  const from = options.from ?? process.cwd();
  const { builtin, relative, bare } = classify(specifier);

  if (builtin) {
    return {
      specifier,
      resolved: specifier.startsWith('node:') ? specifier : `node:${specifier}`,
      url: specifier.startsWith('node:') ? specifier : `node:${specifier}`,
      path: null,
      isBuiltin: true,
      isRelative: false,
      isBare: false,
    };
  }

  const parent = toParentFile(from);
  const require = createRequire(pathToFileURL(parent));

  let resolved;
  try {
    resolved = require.resolve(specifier);
  } catch (err) {
    if (err && err.code === 'MODULE_NOT_FOUND') {
      throw new Error(
        `Cannot resolve "${specifier}" from "${parent}"`,
        { cause: err },
      );
    }
    throw err;
  }

  return {
    specifier,
    resolved,
    url: /^[a-z]+:/.test(resolved) ? resolved : pathToFileURL(resolved).href,
    path: resolved,
    isBuiltin: false,
    isRelative: relative,
    isBare: bare,
  };
}

/**
 * Resolve several specifiers from the same anchor. Unresolvable specifiers are
 * reported per-entry instead of aborting the whole batch.
 *
 * @param {string[]} specifiers
 * @param {{ from?: string }} [options]
 */
export function resolveAll(specifiers, options = {}) {
  return specifiers.map((specifier) => {
    try {
      return { specifier, ok: true, result: resolve(specifier, options) };
    } catch (error) {
      return { specifier, ok: false, error };
    }
  });
}

/**
 * Create a resolver bound to a fixed anchor.
 *
 * @param {{ from?: string }} [options]
 */
export function createResolver(options = {}) {
  const from = options.from ?? process.cwd();
  return {
    from,
    resolve: (specifier) => resolve(specifier, { from }),
    resolveAll: (specifiers) => resolveAll(specifiers, { from }),
  };
}

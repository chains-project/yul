import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'

function toAnchor(parent) {
  if (parent instanceof URL) return parent.href
  return pathToFileURL(parent).href
}

/**
 * Create a resolver anchored at `parent` that follows Node's own module
 * resolution algorithm (the same one behind `require.resolve`).
 *
 * @param {string | URL} [parent] Absolute file path or `file:` URL used as the
 *   resolution anchor. Defaults to the current working directory.
 * @returns {{
 *   resolve: (specifier: string) => string,
 *   resolvePaths: (specifier: string, paths: string[]) => string,
 *   require: NodeRequire,
 * }}
 */
export function createResolver(parent = `${process.cwd()}/`) {
  const require = createRequire(toAnchor(parent))

  return {
    resolve(specifier) {
      return require.resolve(specifier)
    },
    resolvePaths(specifier, paths) {
      return require.resolve(specifier, { paths })
    },
    require,
  }
}

/**
 * Resolve a single `specifier` as if it were required from `parent`.
 *
 * @param {string} specifier
 * @param {string | URL} [parent]
 * @returns {string}
 */
export function resolve(specifier, parent) {
  return createResolver(parent).resolve(specifier)
}

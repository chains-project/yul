import { createResolver } from './resolver.js';

export { createResolver, defaultConditions, nodeModulesPaths, DEFAULT_EXTENSIONS } from './resolver.js';
export { packageExportsResolve, packageImportsResolve, patternKeyCompare } from './package-exports.js';

/**
 * One-off resolution with a fresh (uncached) resolver. Build tools resolving
 * many modules should create a single resolver with `createResolver()` and
 * reuse it so package.json reads and stat calls are cached.
 *
 * @param {string} request
 * @param {string} basedir
 * @param {import('../types/index.d.ts').ResolverOptions} [options]
 */
export function resolve(request, basedir, options) {
  return createResolver(options).resolve(request, basedir);
}

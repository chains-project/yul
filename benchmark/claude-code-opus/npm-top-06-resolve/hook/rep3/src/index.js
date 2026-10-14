import { Resolver } from './resolver.js';

export { Resolver, DEFAULT_CONDITIONS, DEFAULT_EXTENSIONS, nodeModulesPaths } from './resolver.js';
export { nodeFsHost } from './fs-host.js';
export { packageExportsResolve, packageImportsResolve, patternKeyCompare } from './package-exports.js';

/**
 * One-shot convenience wrapper. Build tools resolving many modules should
 * reuse a `Resolver` instance so package.json reads are cached.
 */
export function resolve(request, parentPath, options) {
  return new Resolver(options).resolve(request, parentPath);
}

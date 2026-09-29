import { Resolver } from './resolver.js';

export { Resolver } from './resolver.js';
export {
  ModuleNotFoundError,
  PackagePathNotExportedError,
  PackageImportNotDefinedError,
  InvalidPackageConfigError,
  InvalidModuleSpecifierError,
} from './errors.js';
export { isCoreModule, nodeModulesPaths, parsePackageSpecifier } from './utils.js';

const defaultResolver = new Resolver();

export function createResolver(options) {
  return new Resolver(options);
}

export function resolveSync(request, options = {}) {
  if (options && Object.keys(options).length > 0) {
    return new Resolver(options).resolve(request, options.basedir);
  }
  return defaultResolver.resolve(request);
}

export function resolve(request, options = {}) {
  return Promise.resolve().then(() => resolveSync(request, options));
}

export {
  resolveSync,
  resolveFromFile,
  nodeModulesPaths,
  ResolveError,
  type ResolveOptions,
  type ResolveErrorCode,
} from "./resolve.js";

export {
  readPackage,
  findNearestPackage,
  clearPackageCache,
  type PackageJson,
  type PackageInfo,
} from "./package-json.js";

export {
  resolveExports,
  resolveImports,
  splitPackageSpecifier,
} from "./exports.js";

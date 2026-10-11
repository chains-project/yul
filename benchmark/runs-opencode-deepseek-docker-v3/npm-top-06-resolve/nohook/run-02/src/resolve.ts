import { realpathSync, statSync } from "node:fs";
import { builtinModules } from "node:module";
import { dirname, join, parse, resolve as resolvePath, sep } from "node:path";
import { resolveExports, resolveImports, splitPackageSpecifier } from "./exports.js";
import { findNearestPackage, readPackage, type PackageJson } from "./package-json.js";

export interface ResolveOptions {
  /** Directory that relative specifiers and `node_modules` lookups are resolved from. */
  basedir: string;
  /** File extensions to probe, in order. Defaults to `[".js", ".json", ".node"]`. */
  extensions?: readonly string[];
  /** Package `exports`/`imports` conditions. Defaults to `["node", "require", "default"]`. */
  conditions?: readonly string[];
  /** Extra directories to search after walking `node_modules` up the tree (`NODE_PATH`). */
  paths?: readonly string[];
  /** Skip symlink resolution of the final result. */
  preserveSymlinks?: boolean;
}

export type ResolveErrorCode =
  | "MODULE_NOT_FOUND"
  | "ERR_PACKAGE_PATH_NOT_EXPORTED";

/** Thrown when a specifier cannot be resolved. */
export class ResolveError extends Error {
  readonly code: ResolveErrorCode;

  constructor(message: string, code: ResolveErrorCode) {
    super(message);
    this.name = "ResolveError";
    this.code = code;
  }
}

interface NormalizedOptions {
  basedir: string;
  extensions: readonly string[];
  conditions: readonly string[];
  paths: readonly string[] | undefined;
  preserveSymlinks: boolean;
}

const defaultExtensions = [".js", ".json", ".node"] as const;
const defaultConditions = ["node", "require", "default"] as const;

const builtins = new Set(builtinModules);

function isBuiltin(specifier: string): boolean {
  return specifier.startsWith("node:") || builtins.has(specifier);
}

function isFile(path: string): boolean {
  try {
    return statSync(path).isFile();
  } catch {
    return false;
  }
}

function isDirectory(path: string): boolean {
  try {
    return statSync(path).isDirectory();
  } catch {
    return false;
  }
}

function loadAsFile(path: string, extensions: readonly string[]): string | undefined {
  if (isFile(path)) return path;
  for (const extension of extensions) {
    const candidate = path + extension;
    if (isFile(candidate)) return candidate;
  }
  return undefined;
}

function loadIndex(dir: string, extensions: readonly string[]): string | undefined {
  return loadAsFile(join(dir, "index"), extensions);
}

function legacyMain(pkg: PackageJson): string | undefined {
  return typeof pkg.main === "string" ? pkg.main : undefined;
}

function loadAsDirectory(path: string, options: NormalizedOptions): string | undefined {
  const pkg = readPackage(path);
  const main = pkg ? legacyMain(pkg.data) : undefined;
  if (main) {
    const target = resolvePath(path, main);
    const loaded =
      loadAsFile(target, options.extensions) ??
      loadIndex(target, options.extensions) ??
      loadIndex(path, options.extensions);
    if (loaded) return loaded;
  }
  return loadIndex(path, options.extensions);
}

/** Directories searched for `node_modules`, from the base up to the filesystem root. */
export function nodeModulesPaths(from: string, paths?: readonly string[]): string[] {
  const dirs: string[] = [];
  let current = resolvePath(from);
  const { root } = parse(current);
  for (;;) {
    const segments = current.split(sep);
    if (segments[segments.length - 1] !== "node_modules") {
      dirs.push(join(current, "node_modules"));
    }
    if (current === root) break;
    current = dirname(current);
  }
  if (paths) dirs.push(...paths);
  return dirs;
}

function resolvePackageTarget(
  pkgDir: string,
  pkg: PackageJson,
  subpath: string,
  options: NormalizedOptions,
): string {
  const target = resolveExports(pkg, subpath, options.conditions);
  if (target === undefined) {
    throw new ResolveError(
      `Package subpath '${subpath}' is not defined by "exports" in ${join(pkgDir, "package.json")}`,
      "ERR_PACKAGE_PATH_NOT_EXPORTED",
    );
  }
  const absolute = resolvePath(pkgDir, target);
  return loadAsFile(absolute, options.extensions) ?? absolute;
}

function resolveNodeModules(
  specifier: string,
  options: NormalizedOptions,
): string | undefined {
  const parsed = splitPackageSpecifier(specifier);
  for (const dir of nodeModulesPaths(options.basedir, options.paths)) {
    if (parsed) {
      const packageDir = join(dir, parsed.name);
      if (isDirectory(packageDir)) {
        const pkg = readPackage(packageDir);
        if (pkg && pkg.data.exports !== undefined) {
          return resolvePackageTarget(packageDir, pkg.data, parsed.subpath, options);
        }
      }
    }
    const candidate = join(dir, specifier);
    const file = loadAsFile(candidate, options.extensions);
    if (file) return file;
    const directory = loadAsDirectory(candidate, options);
    if (directory) return directory;
  }
  return undefined;
}

function resolvePackageSelf(
  specifier: string,
  options: NormalizedOptions,
): string | undefined {
  const parsed = splitPackageSpecifier(specifier);
  if (!parsed) return undefined;
  const pkg = findNearestPackage(options.basedir);
  if (!pkg || pkg.data.name !== parsed.name || pkg.data.exports === undefined) {
    return undefined;
  }
  return resolvePackageTarget(pkg.dir, pkg.data, parsed.subpath, options);
}

function resolvePackageImports(
  specifier: string,
  options: NormalizedOptions,
): string | undefined {
  const pkg = findNearestPackage(options.basedir);
  if (!pkg) return undefined;
  const target = resolveImports(pkg.data, specifier, options.conditions);
  if (target === undefined) return undefined;
  if (target.startsWith(".")) {
    const absolute = resolvePath(pkg.dir, target);
    return loadAsFile(absolute, options.extensions) ?? absolute;
  }
  return resolveNodeModules(target, options);
}

function normalize(options: ResolveOptions): NormalizedOptions {
  return {
    basedir: resolvePath(options.basedir),
    extensions: options.extensions ?? defaultExtensions,
    conditions: options.conditions ?? defaultConditions,
    paths: options.paths,
    preserveSymlinks: options.preserveSymlinks ?? false,
  };
}

/**
 * Resolve `specifier` following Node's module resolution algorithm.
 *
 * Handles core modules, relative/absolute paths, `package.json#exports` and
 * `#imports` maps, self-references, and the `node_modules` walk.
 */
export function resolveSync(specifier: string, options: ResolveOptions): string {
  const normalized = normalize(options);
  const { basedir } = normalized;

  if (isBuiltin(specifier)) return specifier;

  let resolved: string | undefined;

  if (
    specifier.startsWith("./") ||
    specifier.startsWith("../") ||
    specifier === "." ||
    specifier === ".." ||
    specifier.startsWith("/")
  ) {
    const base = specifier.startsWith("/") ? specifier : resolvePath(basedir, specifier);
    resolved = loadAsFile(base, normalized.extensions) ?? loadAsDirectory(base, normalized);
  } else if (specifier.startsWith("#")) {
    resolved = resolvePackageImports(specifier, normalized);
  } else {
    resolved =
      resolvePackageSelf(specifier, normalized) ??
      resolveNodeModules(specifier, normalized);
  }

  if (resolved === undefined) {
    throw new ResolveError(
      `Cannot find module '${specifier}' from '${basedir}'`,
      "MODULE_NOT_FOUND",
    );
  }

  if (!normalized.preserveSymlinks) {
    try {
      resolved = realpathSync(resolved);
    } catch {
      // ignore: keep the unresolved path
    }
  }
  return resolved;
}

/** Convenience wrapper resolving relative to the directory of a file. */
export function resolveFromFile(
  fromFile: string,
  specifier: string,
  options: Omit<ResolveOptions, "basedir"> = {},
): string {
  return resolveSync(specifier, { ...options, basedir: dirname(fromFile) });
}

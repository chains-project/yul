import { readFileSync, realpathSync, statSync } from "node:fs";
import { builtinModules } from "node:module";
import path from "node:path";

/**
 * A recursive representation of the `exports` / `imports` field of a
 * package.json file. It can be a plain target string, an array of fallbacks,
 * or a (possibly nested) map of subpaths and/or conditions.
 */
export type PackageMap =
  | string
  | null
  | PackageMap[]
  | { [key: string]: PackageMap };

export interface ResolveOptions {
  /** Directory the request is resolved from. Defaults to `process.cwd()`. */
  basedir?: string;
  /** File extensions tried, in order. Defaults to `[".js", ".json", ".node"]`. */
  extensions?: string[];
  /** Condition names used for `exports`/`imports`. Defaults to `["node", "require"]`. */
  conditions?: string[];
  /** Whether built-in modules resolve to their name. Defaults to `true`. */
  includeCoreModules?: boolean;
  /** Return the real path instead of the symlink path. Defaults to `false`. */
  preserveSymlinks?: boolean;
}

export class ResolveError extends Error {
  readonly code: string;

  constructor(message: string, code = "MODULE_NOT_FOUND") {
    super(message);
    this.name = "ResolveError";
    this.code = code;
  }
}

const DEFAULT_EXTENSIONS = [".js", ".json", ".node"];
const DEFAULT_CONDITIONS = ["node", "require"];

const BUILTIN_MODULES = new Set<string>([
  ...builtinModules,
  ...builtinModules.map((name) => `node:${name}`),
]);

/** Returns true if `id` refers to a Node.js built-in module. */
export function isCoreModule(id: string): boolean {
  return BUILTIN_MODULES.has(id) || id.startsWith("node:");
}

function isFile(target: string): boolean {
  try {
    return statSync(target).isFile();
  } catch {
    return false;
  }
}

function readJson(file: string): Record<string, unknown> | undefined {
  try {
    return JSON.parse(readFileSync(file, "utf8")) as Record<string, unknown>;
  } catch {
    return undefined;
  }
}

function toRealPath(target: string): string {
  try {
    return realpathSync(target);
  } catch {
    return target;
  }
}

function isPathSpecifier(request: string): boolean {
  return (
    request === "." ||
    request === ".." ||
    request.startsWith("./") ||
    request.startsWith("../") ||
    request.startsWith("/") ||
    path.isAbsolute(request)
  );
}

// ---------------------------------------------------------------------------
// LOAD_AS_FILE / LOAD_INDEX
// ---------------------------------------------------------------------------

function loadAsFile(target: string, extensions: string[]): string | undefined {
  if (isFile(target)) return target;
  for (const extension of extensions) {
    const candidate = target + extension;
    if (isFile(candidate)) return candidate;
  }
  return undefined;
}

function loadIndex(directory: string, extensions: string[]): string | undefined {
  for (const extension of extensions) {
    const candidate = path.join(directory, `index${extension}`);
    if (isFile(candidate)) return candidate;
  }
  return undefined;
}

// ---------------------------------------------------------------------------
// exports / imports resolution
// ---------------------------------------------------------------------------

function applyPattern(target: string, match: string | undefined): string {
  return match === undefined ? target : target.split("*").join(match);
}

function resolveTarget(
  target: PackageMap,
  conditions: string[],
  match: string | undefined
): string | undefined {
  if (typeof target === "string") return applyPattern(target, match);

  if (Array.isArray(target)) {
    for (const entry of target) {
      const resolved = resolveTarget(entry, conditions, match);
      if (resolved !== undefined) return resolved;
    }
    return undefined;
  }

  if (target && typeof target === "object") {
    for (const key of Object.keys(target)) {
      if (key === "default" || conditions.includes(key)) {
        const resolved = resolveTarget(target[key], conditions, match);
        if (resolved !== undefined) return resolved;
      }
    }
  }

  return undefined;
}

function resolvePackageMap(
  field: PackageMap,
  subpath: string,
  conditions: string[],
  kind: "exports" | "imports"
): string | undefined {
  if (typeof field === "string" || Array.isArray(field)) {
    const isMain = kind === "exports" ? subpath === "." : false;
    return isMain ? resolveTarget(field, conditions, undefined) : undefined;
  }

  if (!field || typeof field !== "object") return undefined;

  const isSubpathKey = (key: string): boolean =>
    kind === "exports" ? key.startsWith(".") : key.startsWith("#");

  const keys = Object.keys(field).filter(isSubpathKey);

  if (keys.length === 0) {
    return kind === "exports" && subpath === "."
      ? resolveTarget(field, conditions, undefined)
      : undefined;
  }

  if (isSubpathKey(subpath) && Object.prototype.hasOwnProperty.call(field, subpath)) {
    return resolveTarget(field[subpath], conditions, undefined);
  }

  let bestScore = -1;
  let best: string | undefined;
  for (const key of keys) {
    const star = key.indexOf("*");
    if (star === -1) continue;
    const prefix = key.slice(0, star);
    const suffix = key.slice(star + 1);
    if (
      subpath.length >= prefix.length + suffix.length &&
      subpath.startsWith(prefix) &&
      subpath.endsWith(suffix)
    ) {
      const match = subpath.slice(prefix.length, subpath.length - suffix.length);
      const resolved = resolveTarget(field[key], conditions, match);
      const score = prefix.length + suffix.length;
      if (resolved !== undefined && score > bestScore) {
        bestScore = score;
        best = resolved;
      }
    }
  }
  return best;
}

function resolvePackageTarget(
  packageDir: string,
  target: string,
  extensions: string[]
): string | undefined {
  const resolved = path.resolve(packageDir, target);
  const relative = path.relative(packageDir, resolved);
  if (relative.startsWith("..") || path.isAbsolute(relative)) return undefined;
  return loadAsFile(resolved, extensions) ?? loadIndex(resolved, extensions);
}

// ---------------------------------------------------------------------------
// LOAD_AS_DIRECTORY
// ---------------------------------------------------------------------------

function loadAsDirectory(
  directory: string,
  extensions: string[],
  conditions: string[]
): string | undefined {
  const manifestPath = path.join(directory, "package.json");
  if (isFile(manifestPath)) {
    const manifest = readJson(manifestPath);

    if (manifest && manifest.exports != null) {
      const target = resolvePackageMap(
        manifest.exports as PackageMap,
        ".",
        conditions,
        "exports"
      );
      if (target !== undefined && target.startsWith("./")) {
        const resolved = resolvePackageTarget(directory, target, extensions);
        if (resolved) return resolved;
      }
      return undefined;
    }

    const main = manifest?.main;
    if (typeof main === "string" && main.length > 0) {
      const mainPath = path.resolve(directory, main);
      const resolved =
        loadAsFile(mainPath, extensions) ?? loadIndex(mainPath, extensions);
      if (resolved) return resolved;
    }
  }

  return loadIndex(directory, extensions);
}

// ---------------------------------------------------------------------------
// LOAD_NODE_MODULES
// ---------------------------------------------------------------------------

function nodeModulesPaths(start: string): string[] {
  const dirs: string[] = [];
  let current = path.resolve(start);
  for (;;) {
    if (path.basename(current) !== "node_modules") {
      dirs.push(path.join(current, "node_modules"));
    }
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return dirs;
}

function parsePackageSpecifier(specifier: string): {
  name: string;
  subpath: string;
} {
  const parts = specifier.split("/");
  const scoped = specifier.startsWith("@");
  const name = scoped ? parts.slice(0, 2).join("/") : parts[0];
  const rest = parts.slice(scoped ? 2 : 1);
  return { name, subpath: rest.length > 0 ? `./${rest.join("/")}` : "." };
}

function loadNodeModules(
  request: string,
  start: string,
  extensions: string[],
  conditions: string[]
): string | undefined {
  const { name, subpath } = parsePackageSpecifier(request);

  for (const nodeModulesDir of nodeModulesPaths(start)) {
    const packageDir = path.join(nodeModulesDir, name);
    const manifestPath = path.join(packageDir, "package.json");

    if (isFile(manifestPath)) {
      const manifest = readJson(manifestPath);
      if (manifest && manifest.exports != null) {
        const target = resolvePackageMap(
          manifest.exports as PackageMap,
          subpath,
          conditions,
          "exports"
        );
        if (target !== undefined && target.startsWith("./")) {
          const resolved = resolvePackageTarget(packageDir, target, extensions);
          if (resolved) return resolved;
        }
        return undefined;
      }
    }

    const asFile = loadAsFile(path.join(nodeModulesDir, request), extensions);
    if (asFile) return asFile;

    const asDirectory = loadAsDirectory(
      path.join(nodeModulesDir, request),
      extensions,
      conditions
    );
    if (asDirectory) return asDirectory;
  }

  return undefined;
}

// ---------------------------------------------------------------------------
// package self-reference and imports (#)
// ---------------------------------------------------------------------------

function findPackageScope(
  start: string
): { dir: string; manifest: Record<string, unknown> } | undefined {
  let current = path.resolve(start);
  for (;;) {
    const manifestPath = path.join(current, "package.json");
    if (isFile(manifestPath)) {
      const manifest = readJson(manifestPath);
      if (manifest) return { dir: current, manifest };
    }
    const parent = path.dirname(current);
    if (parent === current) return undefined;
    current = parent;
  }
}

function loadPackageSelf(
  request: string,
  basedir: string,
  extensions: string[],
  conditions: string[]
): string | undefined {
  const { name, subpath } = parsePackageSpecifier(request);
  const scope = findPackageScope(basedir);
  if (!scope || scope.manifest.name !== name || scope.manifest.exports == null) {
    return undefined;
  }

  const target = resolvePackageMap(
    scope.manifest.exports as PackageMap,
    subpath,
    conditions,
    "exports"
  );
  if (target === undefined || !target.startsWith("./")) return undefined;
  return resolvePackageTarget(scope.dir, target, extensions);
}

function loadPackageImports(
  request: string,
  basedir: string,
  extensions: string[],
  conditions: string[]
): string | undefined {
  const scope = findPackageScope(basedir);
  const imports = scope?.manifest.imports;
  if (!scope || !imports || typeof imports !== "object" || Array.isArray(imports)) {
    return undefined;
  }

  const target = resolvePackageMap(imports as PackageMap, request, conditions, "imports");
  if (target === undefined) return undefined;

  if (target.startsWith("./")) {
    return resolvePackageTarget(scope.dir, target, extensions);
  }
  return resolveBare(target, scope.dir, extensions, conditions);
}

function resolveBare(
  request: string,
  basedir: string,
  extensions: string[],
  conditions: string[]
): string | undefined {
  return (
    loadPackageSelf(request, basedir, extensions, conditions) ??
    loadNodeModules(request, basedir, extensions, conditions)
  );
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Resolve a module request the way Node.js's CommonJS resolver does, without
 * using `require.resolve` or executing any of the target modules.
 *
 * Implements the documented algorithm: core modules, relative/absolute paths,
 * `LOAD_AS_FILE`, `LOAD_INDEX`, package `main`, the `exports` map (conditions,
 * subpaths and `*` patterns), the `imports` map (`#` specifiers), package
 * self-reference and the `node_modules` lookup.
 */
export function resolve(request: string, options: ResolveOptions = {}): string {
  if (typeof request !== "string" || request.length === 0) {
    throw new ResolveError(
      "The module specifier must be a non-empty string",
      "ERR_INVALID_ARG_VALUE"
    );
  }

  let basedir = path.resolve(options.basedir ?? process.cwd());
  if (isFile(basedir)) basedir = path.dirname(basedir);

  const extensions = options.extensions ?? DEFAULT_EXTENSIONS;
  const conditions = options.conditions ?? DEFAULT_CONDITIONS;
  const includeCoreModules = options.includeCoreModules ?? true;
  const preserveSymlinks = options.preserveSymlinks ?? false;

  if (isCoreModule(request)) {
    if (!includeCoreModules) {
      throw new ResolveError(
        `Cannot resolve core module '${request}'`,
        "ERR_MODULE_NOT_FOUND"
      );
    }
    return request;
  }

  let resolved: string | undefined;

  if (request.startsWith("#")) {
    resolved = loadPackageImports(request, basedir, extensions, conditions);
  } else if (isPathSpecifier(request)) {
    const target = path.resolve(basedir, request);
    resolved =
      loadAsFile(target, extensions) ??
      loadAsDirectory(target, extensions, conditions);
  } else {
    resolved = resolveBare(request, basedir, extensions, conditions);
  }

  if (resolved === undefined) {
    throw new ResolveError(
      `Cannot find module '${request}' from '${basedir}'`,
      "MODULE_NOT_FOUND"
    );
  }

  return preserveSymlinks ? resolved : toRealPath(resolved);
}

/** Alias for {@link resolve} that reads more naturally in build-tool code. */
export const resolveModule = resolve;

import { isBuiltin } from "node:module";
import * as fs from "node:fs";
import * as path from "node:path";

export interface ResolveOptions {
  /** Directory the request is resolved from. Defaults to `process.cwd()`. */
  basedir?: string;
  /** File extensions to try, in order. Defaults to `.js`, `.json`, `.node`. */
  extensions?: string[];
  /** Conditions used to resolve `exports`/`imports` maps. */
  conditions?: string[];
  /** Extra `node_modules` directories to search after the ancestor chain. */
  paths?: string[];
  /** Do not resolve symlinks to their real path. Defaults to `false`. */
  preserveSymlinks?: boolean;
}

export interface PackageJson {
  name?: string;
  main?: string;
  exports?: unknown;
  [key: string]: unknown;
}

interface Context {
  basedir: string;
  extensions: string[];
  conditions: string[];
  extraPaths: string[];
  preserveSymlinks: boolean;
  packageCache: Map<string, PackageJson | null>;
}

const DEFAULT_EXTENSIONS = [".js", ".json", ".node"];
const DEFAULT_CONDITIONS = ["node", "require"];

/**
 * Resolve `request` from `options.basedir` using Node's CommonJS resolution
 * algorithm, returning the absolute path to the resolved file. Built-in
 * modules are returned as-is (e.g. `"fs"`).
 */
export function resolve(request: string, options: ResolveOptions = {}): string {
  if (typeof request !== "string" || request.length === 0) {
    throw new TypeError("request must be a non-empty string");
  }

  const basedir = path.resolve(options.basedir ?? process.cwd());
  const ctx: Context = {
    basedir,
    extensions: options.extensions ?? DEFAULT_EXTENSIONS,
    conditions: options.conditions ?? DEFAULT_CONDITIONS,
    extraPaths: (options.paths ?? []).map((p) => path.resolve(p)),
    preserveSymlinks: options.preserveSymlinks ?? false,
    packageCache: new Map(),
  };

  if (isCore(request)) return request;
  return resolveRequest(request, basedir, ctx);
}

/** Returns `true` for built-in modules, including the `node:` form. */
export function isCoreModule(request: string): boolean {
  return isCore(request);
}

function isCore(request: string): boolean {
  if (request.startsWith("node:")) return isBuiltin(request);
  return isBuiltin(request);
}

function resolveRequest(request: string, basedir: string, ctx: Context): string {
  if (request.startsWith("/") || path.isAbsolute(request)) {
    return loadAsFileOrDirectory(request, ctx) ?? throwNotFound(request, basedir);
  }

  if (
    request === "." ||
    request === ".." ||
    request.startsWith("./") ||
    request.startsWith("../")
  ) {
    const target = path.resolve(basedir, request);
    return loadAsFileOrDirectory(target, ctx) ?? throwNotFound(request, basedir);
  }

  return loadNodeModules(request, basedir, ctx) ?? throwNotFound(request, basedir);
}

function loadAsFileOrDirectory(target: string, ctx: Context): string | null {
  return loadAsFile(target, ctx) ?? loadAsDirectory(target, ctx);
}

function loadAsFile(target: string, ctx: Context): string | null {
  if (isFile(target)) return finalize(target, ctx);
  for (const ext of ctx.extensions) {
    const candidate = target + ext;
    if (isFile(candidate)) return finalize(candidate, ctx);
  }
  return null;
}

function loadAsDirectory(dir: string, ctx: Context): string | null {
  const pkg = readPackage(path.join(dir, "package.json"), ctx);
  if (pkg) {
    if (pkg.exports != null) {
      return resolveExports(pkg, dir, ".", ctx);
    }
    if (typeof pkg.main === "string") {
      const main = path.resolve(dir, pkg.main);
      const resolved = loadAsFile(main, ctx) ?? loadIndex(main, ctx);
      if (resolved) return resolved;
    }
  }
  return loadIndex(dir, ctx);
}

function loadIndex(dir: string, ctx: Context): string | null {
  for (const ext of ctx.extensions) {
    const candidate = path.join(dir, "index" + ext);
    if (isFile(candidate)) return finalize(candidate, ctx);
  }
  return null;
}

function loadNodeModules(
  request: string,
  basedir: string,
  ctx: Context,
): string | null {
  const { pkgName, subpath } = parsePackageRequest(request);

  for (const dir of nodeModulesPaths(basedir, ctx)) {
    if (pkgName) {
      const pkgDir = path.join(dir, ...pkgName.split("/"));
      const pkg = readPackage(path.join(pkgDir, "package.json"), ctx);
      if (pkg?.exports != null) {
        const resolved = resolveExports(pkg, pkgDir, subpath, ctx);
        if (resolved) return resolved;
      }
    }

    const target = path.join(dir, request);
    const resolved = loadAsFile(target, ctx) ?? loadAsDirectory(target, ctx);
    if (resolved) return resolved;
  }

  return null;
}

function nodeModulesPaths(basedir: string, ctx: Context): string[] {
  const dirs: string[] = [];
  let dir = path.resolve(basedir);

  for (;;) {
    if (path.basename(dir) !== "node_modules") {
      dirs.push(path.join(dir, "node_modules"));
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }

  dirs.push(...ctx.extraPaths);
  return dirs;
}

interface PackageRequest {
  pkgName: string | null;
  subpath: string;
}

function parsePackageRequest(request: string): PackageRequest {
  const parts = request.split("/");
  if (request.startsWith("@")) {
    if (parts.length < 2) return { pkgName: null, subpath: "." };
    const pkgName = `${parts[0]}/${parts[1]}`;
    const rest = parts.slice(2);
    return { pkgName, subpath: rest.length ? `./${rest.join("/")}` : "." };
  }
  const pkgName = parts[0] ?? request;
  const rest = parts.slice(1);
  return { pkgName, subpath: rest.length ? `./${rest.join("/")}` : "." };
}

function resolveExports(
  pkg: PackageJson,
  pkgDir: string,
  subpath: string,
  ctx: Context,
): string | null {
  const ex = pkg.exports;
  if (ex == null) return null;

  if (isSubpathMap(ex)) {
    const match = matchSubpath(Object.keys(ex), subpath);
    if (!match) {
      throw moduleNotFound(
        `${pkg.name ?? pkgDir}${subpath === "." ? "" : subpath.slice(1)}`,
        `${subpath} is not defined by "exports" in ${path.join(pkgDir, "package.json")}`,
      );
    }
    const target = (ex as Record<string, unknown>)[match.key];
    return resolveTarget(target, match.pattern, ctx, pkgDir);
  }

  if (subpath !== ".") {
    throw moduleNotFound(
      subpath,
      `Package subpath '${subpath}' is not defined by "exports" in ${path.join(pkgDir, "package.json")}`,
    );
  }
  return resolveTarget(ex, "", ctx, pkgDir);
}

function isSubpathMap(ex: unknown): boolean {
  if (typeof ex !== "object" || ex === null || Array.isArray(ex)) return false;
  return Object.keys(ex).some((key) => key.startsWith("."));
}

interface SubpathMatch {
  key: string;
  pattern: string;
}

function matchSubpath(keys: string[], subpath: string): SubpathMatch | null {
  let best: SubpathMatch | null = null;
  let bestPrefix = -1;

  for (const key of keys) {
    if (key === subpath) return { key, pattern: "" };

    const star = key.indexOf("*");
    if (star === -1) continue;

    const prefix = key.slice(0, star);
    const suffix = key.slice(star + 1);
    if (
      subpath.startsWith(prefix) &&
      subpath.endsWith(suffix) &&
      subpath.length >= prefix.length + suffix.length
    ) {
      const captured = subpath.slice(prefix.length, subpath.length - suffix.length);
      if (prefix.length > bestPrefix) {
        bestPrefix = prefix.length;
        best = { key, pattern: captured };
      }
    }
  }

  return best;
}

function resolveTarget(
  target: unknown,
  pattern: string,
  ctx: Context,
  pkgDir: string,
): string | null {
  if (typeof target === "string") {
    if (!target.startsWith("./")) {
      throw moduleNotFound(
        target,
        `Invalid "exports" target '${target}' in ${path.join(pkgDir, "package.json")}`,
      );
    }
    const rel = pattern ? target.replace(/\*/g, pattern) : target;
    const abs = path.resolve(pkgDir, rel);
    if (!isFile(abs)) return null;
    return finalize(abs, ctx);
  }

  if (Array.isArray(target)) {
    for (const entry of target) {
      const resolved = resolveTarget(entry, pattern, ctx, pkgDir);
      if (resolved) return resolved;
    }
    return null;
  }

  if (typeof target === "object" && target !== null) {
    for (const condition of ctx.conditions) {
      if (Object.prototype.hasOwnProperty.call(target, condition)) {
        const resolved = resolveTarget(
          (target as Record<string, unknown>)[condition],
          pattern,
          ctx,
          pkgDir,
        );
        if (resolved) return resolved;
      }
    }
    return null;
  }

  return null;
}

function readPackage(pkgPath: string, ctx: Context): PackageJson | null {
  const cached = ctx.packageCache.get(pkgPath);
  if (cached !== undefined) return cached;

  let pkg: PackageJson | null = null;
  try {
    const raw = fs.readFileSync(pkgPath, "utf8");
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      pkg = parsed as PackageJson;
    }
  } catch {
    pkg = null;
  }

  ctx.packageCache.set(pkgPath, pkg);
  return pkg;
}

function isFile(target: string): boolean {
  try {
    return fs.statSync(target).isFile();
  } catch {
    return false;
  }
}

function finalize(target: string, ctx: Context): string {
  return ctx.preserveSymlinks ? target : fs.realpathSync(target);
}

function throwNotFound(request: string, basedir: string): never {
  throw moduleNotFound(request, `Cannot find module '${request}' from '${basedir}'`);
}

function moduleNotFound(request: string, message: string): NodeJS.ErrnoException {
  const err = new Error(message) as NodeJS.ErrnoException;
  err.code = "MODULE_NOT_FOUND";
  err.name = "Error";
  (err as { request?: string }).request = request;
  return err;
}

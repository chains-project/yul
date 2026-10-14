/** Minimal synchronous filesystem surface the resolver needs. */
export interface ResolverFileSystem {
  statSync(path: string): { isFile(): boolean; isDirectory(): boolean };
  readFileSync(path: string, encoding: 'utf8'): string;
  realpathSync(path: string): string;
}

export interface ResolverOptions {
  /** Filesystem implementation (e.g. an in-memory fs). Defaults to `node:fs`. */
  fs?: ResolverFileSystem;
  /** Extensions probed for extensionless requests. Defaults to `['.js', '.json', '.node']`. */
  extensions?: readonly string[];
  /** Conditions for "exports"/"imports". Defaults to `defaultConditions()`. "default" always matches. */
  conditions?: readonly string[];
  /** Extra directories searched after the node_modules hierarchy (like NODE_PATH). */
  paths?: readonly string[];
  /** Return symlinked paths as-is instead of their real path (like `--preserve-symlinks`). */
  preserveSymlinks?: boolean;
  /** Resolve Node builtin modules (`fs`, `node:fs`, ...) to their ids. Defaults to `true`. */
  builtins?: boolean;
}

export interface Resolver {
  /**
   * Resolve `request` as `require.resolve` would from a module in `basedir`.
   * Returns an absolute file path, or a builtin module id such as `"fs"` / `"node:test"`.
   * Throws errors with Node-style `code`s (`MODULE_NOT_FOUND`, `ERR_PACKAGE_PATH_NOT_EXPORTED`, ...).
   */
  resolve(request: string, basedir: string): string;
  /** Drop cached stat/realpath/package.json results (e.g. after files change in watch mode). */
  clearCache(): void;
}

export const DEFAULT_EXTENSIONS: readonly string[];
export function createResolver(options?: ResolverOptions): Resolver;
export function resolve(request: string, basedir: string, options?: ResolverOptions): string;
export function defaultConditions(): string[];
export function nodeModulesPaths(from: string): string[];
export function patternKeyCompare(keyA: string, keyB: string): -1 | 0 | 1;

export interface TargetContext {
  conditions: Set<string>;
  resolveBare(specifier: string, packageJsonUrl: URL): URL;
}
export function packageExportsResolve(packageJsonUrl: URL, subpath: string, exports: unknown, ctx: TargetContext): URL;
export function packageImportsResolve(specifier: string, packageJsonUrl: URL, imports: unknown, ctx: TargetContext): URL;

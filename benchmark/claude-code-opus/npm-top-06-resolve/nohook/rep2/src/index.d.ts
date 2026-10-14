import type * as fs from 'node:fs';

export interface ResolverFileSystem {
  statSync(path: string, options: { throwIfNoEntry: false }): Pick<fs.Stats, 'isFile' | 'isDirectory'> | undefined;
  readFileSync(path: string, encoding: 'utf8'): string;
  realpathSync(path: string): string;
}

export interface ResolverOptions {
  /** Filesystem implementation. Defaults to `node:fs`. */
  fs?: ResolverFileSystem;
  /** Export conditions; "default" is always active. Defaults to `["node", "require"]`. */
  conditions?: string[];
  /** Extensions to try, in order. Defaults to `[".js", ".json", ".node"]`. */
  extensions?: string[];
  /** Like `--preserve-symlinks`. Defaults to `false` (results are realpath'd). */
  preserveSymlinks?: boolean;
  /** Extra lookup directories searched after the node_modules hierarchy (like NODE_PATH). */
  paths?: string[];
  /** Decides which specifiers are core modules. Defaults to `module.isBuiltin`. */
  isBuiltin?: (specifier: string) => boolean;
}

export interface Resolver {
  /**
   * Resolve `request` as `require.resolve` would from the file at `parent`.
   * Returns an absolute path, or the specifier itself for builtins.
   */
  resolve(request: string, parent: string): string;
  nodeModulesPaths(dir: string): string[];
  /** Drop cached package.json contents. */
  clearCache(): void;
}

export function createResolver(options?: ResolverOptions): Resolver;
export function resolve(request: string, parent: string): string;
export function nodeModulesPaths(dir: string): string[];
export function patternKeyCompare(a: string, b: string): -1 | 0 | 1;
export function packageExportsResolve(
  pkgDir: string,
  subpath: string,
  exports: unknown,
  conditions: Set<string>,
  resolveBare: (specifier: string, pkgDir: string) => string,
): string;
export function packageImportsResolve(
  pkgDir: string,
  specifier: string,
  imports: unknown,
  conditions: Set<string>,
  resolveBare: (specifier: string, pkgDir: string) => string,
): string;

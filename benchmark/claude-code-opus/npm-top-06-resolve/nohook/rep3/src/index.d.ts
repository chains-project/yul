/** The subset of node:fs the resolver reads through. memfs etc. are compatible. */
export interface ResolverFileSystem {
  statSync(path: string, options: { throwIfNoEntry: false }): { isDirectory(): boolean } | undefined;
  readFileSync(path: string, encoding: 'utf8'): string;
  realpathSync(path: string): string;
}

export interface ResolverOptions {
  /** Filesystem to resolve against. Defaults to node:fs. */
  fs?: ResolverFileSystem;
  /** Extensions probed for extensionless files, in order. Defaults to ['.js', '.json', '.node']. */
  extensions?: readonly string[];
  /**
   * Conditions matched in "exports"/"imports" ("default" always matches).
   * Defaults to defaultConditions(): the set require() uses in this Node process.
   */
  conditions?: readonly string[];
  /** Mirror `node --preserve-symlinks`: return symlink paths instead of realpaths. */
  preserveSymlinks?: boolean;
  /** Extra directories searched after node_modules (Node's NODE_PATH etc.). Defaults to []. */
  globalPaths?: readonly string[];
}

export interface Resolver {
  /**
   * Equivalent of `createRequire(parent).resolve(request)`.
   * Returns an absolute path, or the specifier itself for builtin modules.
   * Throws errors with the same `code`s Node uses (MODULE_NOT_FOUND, ERR_PACKAGE_PATH_NOT_EXPORTED, ...).
   */
  resolve(request: string, parent: string | URL): string;
  /** Directories that would be searched for `request` from `parent`. */
  lookupPaths(request: string, parent: string | URL): string[];
  /** Drop cached stat/realpath/package.json results. */
  clearCache(): void;
}

export function createResolver(options?: ResolverOptions): Resolver;
export function resolve(request: string, parent: string | URL, options?: ResolverOptions): string;
export function defaultConditions(): string[];
export function nodeModulesPaths(from: string): string[];
export function patternKeyCompare(a: string, b: string): -1 | 0 | 1;

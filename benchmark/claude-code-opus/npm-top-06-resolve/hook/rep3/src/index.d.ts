/** Minimal filesystem interface the resolver needs. All methods are synchronous. */
export interface FileSystemHost {
  /** "directory" for directories, "file" for anything else that exists, undefined if missing. */
  stat(path: string): 'file' | 'directory' | undefined;
  /** UTF-8 contents, or undefined if the file does not exist. */
  readFile(path: string): string | undefined;
  /** Canonical path with symlinks resolved. Only called on paths that exist. */
  realpath(path: string): string;
}

export interface ResolverOptions {
  /** Defaults to the real filesystem via `node:fs`. */
  fs?: FileSystemHost;
  /** Extensions tried for extensionless requests. Default: [".js", ".json", ".node"]. */
  extensions?: readonly string[];
  /** "exports"/"imports" conditions. Default: ["require", "node"] plus "module-sync" when supported. */
  conditions?: readonly string[];
  /** Equivalent to `--preserve-symlinks`. Default: false. */
  preserveSymlinks?: boolean;
  /** Extra directories searched after node_modules lookups (like NODE_PATH / global folders). */
  paths?: readonly string[];
}

export class Resolver {
  constructor(options?: ResolverOptions);
  /**
   * Resolves `request` as `require.resolve` would from `parentPath`.
   * Returns an absolute file path, or the builtin id for core modules.
   * Throws errors with Node's `code` values (MODULE_NOT_FOUND, ERR_PACKAGE_PATH_NOT_EXPORTED, …).
   */
  resolve(request: string, parentPath: string): string;
  clearCache(): void;
}

export function resolve(request: string, parentPath: string, options?: ResolverOptions): string;

export const DEFAULT_CONDITIONS: readonly string[];
export const DEFAULT_EXTENSIONS: readonly string[];
export const nodeFsHost: FileSystemHost;
export function nodeModulesPaths(from: string): string[];

export interface ExportsContext {
  pjsonURL: URL;
  conditions: Set<string>;
  packageResolve(specifier: string, pjsonURL: URL): URL;
}
export function packageExportsResolve(subpath: string, exports: unknown, ctx: ExportsContext): URL;
export function packageImportsResolve(specifier: string, imports: unknown, ctx: ExportsContext): URL;
export function patternKeyCompare(a: string, b: string): -1 | 0 | 1;

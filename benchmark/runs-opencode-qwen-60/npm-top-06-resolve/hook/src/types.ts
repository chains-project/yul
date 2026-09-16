export interface ResolveOptions {
  /** Base directory to resolve from (defaults to current working directory) */
  basedir?: string;
  /** List of file extensions to try */
  extensions?: string[];
  /** Module conditions for package.json exports */
  conditions?: string[];
  /** Whether to include core modules */
  includeCoreModules?: boolean;
  /** Whether to read package.json files */
  readPackage?: boolean;
  /** Custom conditions for package.json "exports" field */
  mainFields?: string[];
  /** File name candidates in order of preference */
  fileExtensions?: string[];
  /** Custom file filter */
  isFile?: (path: string) => boolean;
  /** Custom directory check */
  isDirectory?: (path: string) => boolean;
  /** Custom file read function */
  readFile?: (path: string) => string | null;
  /** Custom stat function */
  stat?: (path: string) => { isFile(): boolean; isDirectory(): boolean } | null;
}

export interface ResolveResult {
  /** The resolved file path */
  path: string;
  /** The package.json path if this is a package resolution */
  packagePath?: string;
  /** Package.json content if available */
  packageJson?: Record<string, unknown>;
}

export interface ResolveError extends Error {
  code: string;
  path?: string;
  siblingWithExtension?: string;
}

export type ResolveFunction = (
  specifier: string,
  options?: ResolveOptions
) => Promise<ResolveResult>;
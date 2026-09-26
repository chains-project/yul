import resolve from "resolve";

export interface ResolveOptions {
  /** Directory to resolve `specifier` from, as if a module lived there. */
  basedir: string;
  /** File extensions to try, in order, when `specifier` has none. */
  extensions?: string[];
  /** Extra directory names to search besides `node_modules`. */
  moduleDirectory?: string | string[];
  /** Don't resolve `basedir` to its real path before searching (mirrors `node --preserve-symlinks`). */
  preserveSymlinks?: boolean;
}

export class ModuleNotFoundError extends Error {
  constructor(
    public readonly specifier: string,
    public readonly basedir: string,
    cause: unknown,
  ) {
    super(`Cannot find module '${specifier}' from '${basedir}'`, { cause });
    this.name = "ModuleNotFoundError";
  }
}

function toResolveOpts(options: ResolveOptions): resolve.Opts {
  return {
    basedir: options.basedir,
    extensions: options.extensions,
    moduleDirectory: options.moduleDirectory,
    preserveSymlinks: options.preserveSymlinks,
  };
}

/** Returns true if `specifier` names a Node builtin (e.g. "fs", "node:path"). */
export function isCoreModule(specifier: string): boolean {
  return Boolean(resolve.isCore(specifier));
}

/**
 * Resolve `specifier` to an absolute path using Node's CommonJS algorithm
 * (relative/absolute paths, package "main", node_modules walk up the tree).
 */
export function resolveModule(specifier: string, options: ResolveOptions): string {
  try {
    return resolve.sync(specifier, toResolveOpts(options));
  } catch (err) {
    throw new ModuleNotFoundError(specifier, options.basedir, err);
  }
}

/** Async counterpart of {@link resolveModule}. */
export function resolveModuleAsync(specifier: string, options: ResolveOptions): Promise<string> {
  return new Promise((resolvePromise, reject) => {
    resolve(specifier, toResolveOpts(options), (err, resolved) => {
      if (err || !resolved) {
        reject(new ModuleNotFoundError(specifier, options.basedir, err));
        return;
      }
      resolvePromise(resolved);
    });
  });
}

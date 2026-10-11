export class ModuleNotFoundError extends Error {
  readonly code = "MODULE_NOT_FOUND";
  readonly specifier: string;
  readonly basedir: string;

  constructor(specifier: string, basedir: string, options?: { cause?: unknown }) {
    super(`Cannot find module '${specifier}' from '${basedir}'`);
    this.name = "ModuleNotFoundError";
    this.specifier = specifier;
    this.basedir = basedir;
    if (options?.cause !== undefined) {
      this.cause = options.cause;
    }
  }
}

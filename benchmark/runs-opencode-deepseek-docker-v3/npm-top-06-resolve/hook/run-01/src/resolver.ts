import fs from "node:fs";
import { isBuiltin } from "node:module";
import process from "node:process";
import enhancedResolve from "enhanced-resolve";
import { ModuleNotFoundError } from "./errors.js";

const { CachedInputFileSystem, ResolverFactory } = enhancedResolve;

export type AliasMap = Record<string, string | string[] | false>;

export interface ResolverOptions {
  extensions?: string[];
  conditionNames?: string[];
  mainFields?: (string | string[])[];
  mainFiles?: string[];
  modules?: string[];
  alias?: AliasMap;
  fallback?: AliasMap;
  exportsFields?: (string | string[])[];
  importsFields?: (string | string[])[];
  symlinks?: boolean;
  fileSystem?: enhancedResolve.FileSystem;
  tsconfig?: boolean | string;
}

export interface ResolveQuery {
  basedir?: string;
}

const DEFAULT_EXTENSIONS = [".js", ".json", ".node"];
const DEFAULT_CONDITION_NAMES = ["node", "require", "default"];
const DEFAULT_MAIN_FIELDS = ["main"];
const DEFAULT_MAIN_FILES = ["index"];
const DEFAULT_MODULES = ["node_modules"];

function toResolveOptions(
  options: ResolverOptions,
  fileSystem: enhancedResolve.FileSystem,
  useSyncFileSystemCalls: boolean,
): enhancedResolve.ResolveOptions {
  return {
    fileSystem,
    extensions: options.extensions ?? DEFAULT_EXTENSIONS,
    conditionNames: options.conditionNames ?? DEFAULT_CONDITION_NAMES,
    mainFields: options.mainFields ?? DEFAULT_MAIN_FIELDS,
    mainFiles: options.mainFiles ?? DEFAULT_MAIN_FILES,
    modules: options.modules ?? DEFAULT_MODULES,
    alias: options.alias,
    fallback: options.fallback,
    exportsFields: options.exportsFields ?? [["exports"]],
    importsFields: options.importsFields ?? [["imports"]],
    symlinks: options.symlinks ?? true,
    tsconfig: options.tsconfig,
    useSyncFileSystemCalls,
  };
}

function isCoreModule(specifier: string): boolean {
  return specifier.startsWith("node:") || isBuiltin(specifier);
}

export class Resolver {
  readonly #async: enhancedResolve.Resolver;
  readonly #sync: enhancedResolve.Resolver;

  constructor(options: ResolverOptions = {}) {
    const fileSystem =
      options.fileSystem ??
      new CachedInputFileSystem(
        fs as unknown as enhancedResolve.BaseFileSystem,
        4000,
      );
    this.#async = ResolverFactory.createResolver(
      toResolveOptions(options, fileSystem, false),
    );
    this.#sync = ResolverFactory.createResolver(
      toResolveOptions(options, fileSystem, true),
    );
  }

  resolve(specifier: string, query: ResolveQuery = {}): Promise<string> {
    const basedir = query.basedir ?? process.cwd();
    if (isCoreModule(specifier)) {
      return Promise.resolve(specifier);
    }
    return new Promise<string>((resolve, reject) => {
      this.#async.resolve({}, basedir, specifier, (err, result) => {
        if (err) {
          reject(new ModuleNotFoundError(specifier, basedir, { cause: err }));
        } else if (!result) {
          reject(new ModuleNotFoundError(specifier, basedir));
        } else {
          resolve(result);
        }
      });
    });
  }

  resolveSync(specifier: string, query: ResolveQuery = {}): string {
    const basedir = query.basedir ?? process.cwd();
    if (isCoreModule(specifier)) {
      return specifier;
    }
    try {
      const result = this.#sync.resolveSync({}, basedir, specifier);
      if (!result) {
        throw new ModuleNotFoundError(specifier, basedir);
      }
      return result;
    } catch (err) {
      if (err instanceof ModuleNotFoundError) {
        throw err;
      }
      throw new ModuleNotFoundError(specifier, basedir, { cause: err });
    }
  }
}

export function createResolver(options: ResolverOptions = {}): Resolver {
  return new Resolver(options);
}

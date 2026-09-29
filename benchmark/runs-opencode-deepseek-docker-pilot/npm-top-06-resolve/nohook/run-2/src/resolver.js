import fs from 'node:fs';
import path from 'node:path';

import {
  ModuleNotFoundError,
  PackageImportNotDefinedError,
  PackagePathNotExportedError,
  InvalidModuleSpecifierError,
} from './errors.js';
import { resolvePackageMap } from './package-targets.js';
import {
  isCoreModule,
  isDirectory,
  isFile,
  isPathInside,
  nodeModulesPaths,
  parsePackageSpecifier,
} from './utils.js';

const DEFAULT_EXTENSIONS = ['.js', '.json', '.node'];
const DEFAULT_CONDITIONS = ['node', 'require'];

export class Resolver {
  constructor(options = {}) {
    this.basedir = path.resolve(options.basedir ?? process.cwd());
    this.extensions = [...(options.extensions ?? DEFAULT_EXTENSIONS)];
    this.conditions = [...(options.conditions ?? DEFAULT_CONDITIONS)];
    this.preserveSymlinks = options.preserveSymlinks ?? false;
    this.packageCache = new Map();
  }

  resolve(request, basedir = this.basedir) {
    if (typeof request !== 'string' || request.length === 0) {
      throw new TypeError('The "request" argument must be a non-empty string');
    }

    if (request.startsWith('node:') || isCoreModule(request)) {
      return request;
    }

    const start = path.resolve(basedir);
    let resolved;

    if (request.startsWith('#')) {
      resolved = this.#resolvePackageImport(request, start);
    } else if (path.isAbsolute(request)) {
      resolved = this.#loadAsFileOrDirectory(request);
    } else if (
      request === '.' ||
      request === '..' ||
      request.startsWith('./') ||
      request.startsWith('../')
    ) {
      resolved = this.#loadAsFileOrDirectory(path.resolve(start, request));
    } else {
      resolved = this.#loadNodeModules(request, start);
    }

    if (!resolved) {
      throw new ModuleNotFoundError(request, nodeModulesPaths(start));
    }
    return this.#finalize(resolved);
  }

  readPackageJson(packagePath) {
    if (this.packageCache.has(packagePath)) {
      return this.packageCache.get(packagePath);
    }
    let parsed = null;
    try {
      const raw = fs.readFileSync(packagePath, 'utf8');
      parsed = JSON.parse(raw);
      if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
        parsed = null;
      }
    } catch (error) {
      if (error.code !== 'ENOENT' && !(error instanceof SyntaxError)) {
        throw error;
      }
      parsed = null;
    }
    this.packageCache.set(packagePath, parsed);
    return parsed;
  }

  #finalize(file) {
    if (this.preserveSymlinks) return file;
    try {
      return fs.realpathSync.native(file);
    } catch {
      return file;
    }
  }

  #loadAsFile(base) {
    if (isFile(base)) return base;
    for (const extension of this.extensions) {
      const candidate = base + extension;
      if (isFile(candidate)) return candidate;
    }
    return null;
  }

  #loadIndex(directory) {
    for (const extension of this.extensions) {
      const candidate = path.join(directory, `index${extension}`);
      if (isFile(candidate)) return candidate;
    }
    return null;
  }

  #loadAsDirectory(directory) {
    if (!isDirectory(directory)) return null;

    const packagePath = path.join(directory, 'package.json');
    if (isFile(packagePath)) {
      const pkg = this.readPackageJson(packagePath);
      const main = pkg?.main;
      if (typeof main === 'string' && main.length > 0) {
        const mainBase = path.resolve(directory, main);
        const resolved = this.#loadAsFile(mainBase) ?? this.#loadIndex(mainBase);
        if (resolved) return resolved;
      }
    }

    return this.#loadIndex(directory);
  }

  #loadAsFileOrDirectory(base) {
    return this.#loadAsFile(base) ?? this.#loadAsDirectory(base);
  }

  #loadNodeModules(request, start) {
    const { packageName, subpath } = parsePackageSpecifier(request);
    if (!packageName) return null;

    for (const modulesDir of nodeModulesPaths(start)) {
      const packageDir = path.join(modulesDir, packageName);
      if (!isDirectory(packageDir)) continue;
      const resolved = this.#resolvePackageEntry(packageDir, subpath);
      if (resolved) return resolved;
    }
    return null;
  }

  #resolvePackageEntry(packageDir, subpath) {
    const packagePath = path.join(packageDir, 'package.json');
    const pkg = isFile(packagePath) ? this.readPackageJson(packagePath) : null;

    if (pkg && pkg.exports !== undefined) {
      const request = subpath === '' ? '.' : `./${subpath}`;
      const target = resolvePackageMap(pkg.exports, request, this.conditions, 'exports');
      if (target == null) {
        throw new PackagePathNotExportedError(packagePath, request);
      }
      return this.#resolveTarget(packageDir, packagePath, target, request);
    }

    if (subpath === '') {
      return this.#loadAsDirectory(packageDir);
    }

    const base = path.resolve(packageDir, subpath);
    if (!isPathInside(packageDir, base)) {
      throw new InvalidModuleSpecifierError(`${packageDir}/${subpath}`);
    }
    return this.#loadAsFileOrDirectory(base);
  }

  #resolveTarget(packageDir, packagePath, target, request) {
    if (!target.startsWith('./')) {
      throw new InvalidModuleSpecifierError(request, 'invalid "exports" target');
    }
    const targetPath = path.resolve(packageDir, target);
    if (!isPathInside(packageDir, targetPath)) {
      throw new InvalidModuleSpecifierError(request, 'target escapes package directory');
    }
    const resolved = this.#loadAsFileOrDirectory(targetPath);
    if (!resolved) {
      throw new ModuleNotFoundError(request, [packageDir]);
    }
    return resolved;
  }

  #findPackageScope(from) {
    let directory = path.resolve(from);
    const { root } = path.parse(directory);

    for (;;) {
      if (path.basename(directory) === 'node_modules') return null;
      const candidate = path.join(directory, 'package.json');
      if (isFile(candidate)) return candidate;
      if (directory === root) return null;
      directory = path.dirname(directory);
    }
  }

  #resolvePackageImport(request, start) {
    const packagePath = this.#findPackageScope(start);
    if (!packagePath) {
      throw new PackageImportNotDefinedError(request, null);
    }
    const pkg = this.readPackageJson(packagePath);
    if (!pkg || pkg.imports === undefined) {
      throw new PackageImportNotDefinedError(request, packagePath);
    }
    const target = resolvePackageMap(pkg.imports, request, this.conditions, 'imports');
    if (target == null) {
      throw new PackageImportNotDefinedError(request, packagePath);
    }
    return this.#resolveTarget(path.dirname(packagePath), packagePath, target, request);
  }
}

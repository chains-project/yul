import { promises as fs } from 'fs';
import path from 'path';
import { ResolveOptions, ResolveResult, ResolveError, ResolveFunction } from './types.js';

const DEFAULT_EXTENSIONS = ['.js', '.json', '.node'];
const DEFAULT_CONDITIONS = ['node', 'require'];
const DEFAULT_MAIN_FIELDS = ['main'];

const CORE_MODULES = new Set([
  '_http_agent', '_http_client', '_http_common', '_http_incoming',
  '_http_server', '_http_wrap', '_tls_common', '_tls_wrap',
  'assert', 'assert/strict', 'async_hooks', 'buffer', 'child_process',
  'cluster', 'console', 'constants', 'crypto', 'dgram', 'diagnostics_channel',
  'dns', 'dns/promises', 'domain', 'events', 'fs', 'fs/promises',
  'http', 'http2', 'https', 'inspector', 'inspector/promises',
  'module', 'net', 'os', 'path', 'path/posix', 'path/win32',
  'perf_hooks', 'process', 'punycode', 'querystring', 'readline',
  'readline/promises', 'repl', 'stream', 'stream/promises',
  'string_decoder', 'sys', 'timers', 'timers/promises', 'tls', 'trace_events',
  'tty', 'url', 'util', 'util/types', 'v8', 'vm', 'wasi', 'worker_threads',
  'zlib', 'path/win32', 'path/posix', 'lint', 'onboarding', 'sea', 'sqlite',
  'test', 'v8/platform'
]);

function createResolveError(code: string, message: string, path?: string, sibling?: string): ResolveError {
  const error = new Error(message) as ResolveError;
  error.code = code;
  error.path = path;
  if (sibling) {
    error.siblingWithExtension = sibling;
  }
  return error;
}

async function stat(filepath: string): Promise<{ isFile(): boolean; isDirectory(): boolean } | null> {
  try {
    const stats = await fs.stat(filepath);
    return {
      isFile: () => stats.isFile(),
      isDirectory: () => stats.isDirectory()
    };
  } catch {
    return null;
  }
}

async function readFile(filepath: string): Promise<string | null> {
  try {
    return await fs.readFile(filepath, 'utf-8');
  } catch {
    return null;
  }
}

function tryParsePackageJson(content: string): Record<string, unknown> | null {
  try {
    return JSON.parse(content);
  } catch {
    return null;
  }
}

async function resolvePackageExports(
  packagePath: string,
  subpath: string,
  conditions: string[],
  mainFields: string[]
): Promise<string | null> {
  const packageJsonPath = path.join(packagePath, 'package.json');
  const content = await readFile(packageJsonPath);
  if (!content) return null;

  const pkg = tryParsePackageJson(content);
  if (!pkg?.exports) return null;

  const exportsField = pkg.exports as Record<string, unknown> | string | unknown[];

  if (typeof exportsField === 'string') {
    return path.resolve(packagePath, exportsField);
  }

  if (Array.isArray(exportsField)) {
    for (const condition of exportsField) {
      if (typeof condition === 'string') return path.resolve(packagePath, condition);
    }
    return null;
  }

  if (typeof exportsField === 'object') {
    const target = exportsField[subpath] ?? exportsField['.'];
    if (!target) return null;

    if (typeof target === 'string') {
      return path.resolve(packagePath, target);
    }

    if (Array.isArray(target)) {
      for (const cond of conditions) {
        const match = target.find((t: unknown) => {
          if (typeof t === 'object' && t !== null) {
            return cond in (t as Record<string, unknown>);
          }
          return typeof t === 'string';
        });
        if (typeof match === 'string') return path.resolve(packagePath, match);
        if (typeof match === 'object' && match !== null) {
          for (const key of Object.keys(match as Record<string, unknown>)) {
            if (conditions.includes(key)) {
              return path.resolve(packagePath, (match as Record<string, string>)[key]);
            }
          }
        }
      }
      return null;
    }

    if (typeof target === 'object') {
      for (const cond of conditions) {
        if (cond in (target as Record<string, unknown>)) {
          const value = (target as Record<string, string>)[cond];
          if (typeof value === 'string') return path.resolve(packagePath, value);
        }
      }
      for (const key of mainFields) {
        if (key in (target as Record<string, unknown>)) {
          const value = (target as Record<string, string>)[key];
          if (typeof value === 'string') return path.resolve(packagePath, value);
        }
      }
    }
  }

  return null;
}

async function loadPackageInfo(basedir: string): Promise<{ path: string; json: Record<string, unknown> } | null> {
  let dir = basedir;
  while (true) {
    const packageJsonPath = path.join(dir, 'package.json');
    const content = await readFile(packageJsonPath);
    if (content) {
      const pkg = tryParsePackageJson(content);
      if (pkg) {
        return { path: dir, json: pkg };
      }
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

async function resolveAsFile(requestPath: string): Promise<string | null> {
  const existing = await stat(requestPath);
  if (existing?.isFile()) return requestPath;
  return null;
}

async function resolveWithExtensions(requestPath: string, extensions: string[]): Promise<string | null> {
  for (const ext of extensions) {
    const withExt = `${requestPath}${ext}`;
    const result = await resolveAsFile(withExt);
    if (result) return result;
  }
  return null;
}

async function resolveAsPackage(requestPath: string, basedir: string, options: ResolveOptions): Promise<ResolveResult | null> {
  const packageInfo = await loadPackageInfo(basedir);
  if (!packageInfo) return null;

  const pkg = packageInfo.json;
  const conditions = options.conditions ?? DEFAULT_CONDITIONS;
  const mainFields = options.mainFields ?? DEFAULT_MAIN_FIELDS;

  const subpath = requestPath;
  if (pkg.exports) {
    const resolvedPath = await resolvePackageExports(
      packageInfo.path,
      subpath,
      conditions,
      mainFields
    );
    if (resolvedPath) {
      return {
        path: resolvedPath,
        packagePath: packageInfo.path,
        packageJson: pkg
      };
    }
  }

  for (const mainField of mainFields) {
    if (mainField in pkg) {
      const mainPath = (pkg[mainField] as string);
      const fullMainPath = path.resolve(packageInfo.path, mainPath);
      const statResult = await stat(fullMainPath);
      if (statResult?.isFile()) {
        return {
          path: fullMainPath,
          packagePath: packageInfo.path,
          packageJson: pkg
        };
      }
      const withExtensions = await resolveWithExtensions(fullMainPath, options.extensions ?? DEFAULT_EXTENSIONS);
      if (withExtensions) {
        return {
          path: withExtensions,
          packagePath: packageInfo.path,
          packageJson: pkg
        };
      }
    }
  }

  return null;
}

async function resolveDirectory(requestPath: string, options: ResolveOptions): Promise<string | null> {
  const indexFiles = options.extensions ?? DEFAULT_EXTENSIONS;
  for (const ext of indexFiles) {
    const indexPath = path.join(requestPath, `index${ext}`);
    const result = await resolveAsFile(indexPath);
    if (result) return result;
  }
  return null;
}

async function lookupPath(requestPath: string, options: ResolveOptions): Promise<ResolveResult | null> {
  const statResult = await stat(requestPath);
  if (statResult?.isFile()) {
    return { path: requestPath };
  }

  if (statResult?.isDirectory()) {
    const dirResult = await resolveDirectory(requestPath, options);
    if (dirResult) return dirResult;
    const pkgResult = await resolveAsPackage(requestPath, requestPath, options);
    if (pkgResult) return pkgResult;
    return null;
  }

  const withExtensions = await resolveWithExtensions(requestPath, options.extensions ?? DEFAULT_EXTENSIONS);
  if (withExtensions) {
    return { path: withExtensions };
  }

  const pkgResult = await resolveAsPackage(requestPath, path.dirname(requestPath), options);
  if (pkgResult) return pkgResult;

  return null;
}

export function createResolver(options?: Partial<ResolveOptions>): ResolveFunction {
  const baseOptions: ResolveOptions = {
    basedir: process.cwd(),
    extensions: DEFAULT_EXTENSIONS,
    conditions: DEFAULT_CONDITIONS,
    includeCoreModules: true,
    readPackage: true,
    mainFields: DEFAULT_MAIN_FIELDS,
    ...options
  };

  return async function resolve(specifier: string, overrideOptions?: ResolveOptions): Promise<ResolveResult> {
    const mergedOptions: ResolveOptions = { ...baseOptions, ...overrideOptions };
    const basedir = mergedOptions.basedir ?? process.cwd();

    if (CORE_MODULES.has(specifier) && mergedOptions.includeCoreModules) {
      throw createResolveError('MODULE_NOT_FOUND', `Cannot find module '${specifier}'`, specifier);
    }

    if (path.isAbsolute(specifier)) {
      const result = await lookupPath(specifier, mergedOptions);
      if (result) return result;
      throw createResolveError('MODULE_NOT_FOUND', `Cannot resolve '${specifier}'`);
    }

    if (specifier.startsWith('./') || specifier.startsWith('../')) {
      const resolvedPath = path.resolve(basedir, specifier);
      const result = await lookupPath(resolvedPath, mergedOptions);
      if (result) return result;
      const error = createResolveError('MODULE_NOT_FOUND', `Cannot resolve relative module '${specifier}'`, specifier);
      throw error;
    }

    const parts = specifier.split('/');
    const scope = parts[0]?.startsWith('@') ? `${parts.shift()}/${parts.shift()}` : parts.shift();
    const moduleName = scope ? `${scope}/${parts.join('/')}` : specifier;

    let searchPath = basedir;
    while (true) {
      const nodeModulesPath = path.join(searchPath, 'node_modules', moduleName);
      const result = await lookupPath(nodeModulesPath, mergedOptions);
      if (result) return result;

      const parent = path.dirname(searchPath);
      if (parent === searchPath) break;
      searchPath = parent;
    }

    throw createResolveError('MODULE_NOT_FOUND', `Cannot resolve module '${specifier}' from '${basedir}'`);
  };
}

export const resolve: ResolveFunction = createResolver();
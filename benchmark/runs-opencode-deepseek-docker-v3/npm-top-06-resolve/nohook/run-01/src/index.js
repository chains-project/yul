import fs from 'node:fs';
import path from 'node:path';
import { isBuiltin } from 'node:module';

const FILE_EXTENSIONS = ['.js', '.json', '.node'];
const INDEX_BASENAMES = ['index.js', 'index.json', 'index.node'];

export class ModuleNotFoundError extends Error {
  constructor(request, fromDir) {
    super(`Cannot find module '${request}' from '${fromDir}'`);
    this.name = 'ModuleNotFoundError';
    this.code = 'MODULE_NOT_FOUND';
    this.request = request;
    this.fromDir = fromDir;
  }
}

function isFile(candidate) {
  try {
    return fs.statSync(candidate).isFile();
  } catch {
    return false;
  }
}

function isDirectory(candidate) {
  try {
    return fs.statSync(candidate).isDirectory();
  } catch {
    return false;
  }
}

function readPackageJson(dir) {
  const file = path.join(dir, 'package.json');
  if (!isFile(file)) return null;
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (cause) {
    throw new SyntaxError(`Invalid package.json at ${file}: ${cause.message}`);
  }
}

function loadAsFile(base) {
  if (isFile(base)) return base;
  for (const extension of FILE_EXTENSIONS) {
    const candidate = base + extension;
    if (isFile(candidate)) return candidate;
  }
  return null;
}

function loadIndex(dir) {
  for (const basename of INDEX_BASENAMES) {
    const candidate = path.join(dir, basename);
    if (isFile(candidate)) return candidate;
  }
  return null;
}

function loadAsDirectory(dir) {
  if (!isDirectory(dir)) return null;
  const pkg = readPackageJson(dir);
  if (pkg && pkg.main) {
    const main = path.resolve(dir, pkg.main);
    const asFile = loadAsFile(main);
    if (asFile) return asFile;
    const asIndex = loadIndex(main);
    if (asIndex) return asIndex;
  }
  return loadIndex(dir);
}

function nodeModulesPaths(startDir) {
  const paths = [];
  let current = path.resolve(startDir);
  for (;;) {
    if (path.basename(current) !== 'node_modules') {
      paths.push(path.join(current, 'node_modules'));
    }
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return paths;
}

function loadNodeModules(request, startDir) {
  for (const dir of nodeModulesPaths(startDir)) {
    const candidate = path.join(dir, request);
    const asFile = loadAsFile(candidate);
    if (asFile) return asFile;
    const asDirectory = loadAsDirectory(candidate);
    if (asDirectory) return asDirectory;
  }
  return null;
}

function baseDirFrom(options) {
  if (options.basedir) return path.resolve(options.basedir);
  if (options.from) {
    const from = path.resolve(options.from);
    return isDirectory(from) ? from : path.dirname(from);
  }
  return process.cwd();
}

function finish(result, request, fromDir) {
  if (result) return result;
  throw new ModuleNotFoundError(request, fromDir);
}

export function resolve(request, options = {}) {
  if (typeof request !== 'string' || request.length === 0) {
    throw new TypeError('request must be a non-empty string');
  }

  const fromDir = baseDirFrom(options);

  if (isBuiltin(request)) return request;

  if (path.isAbsolute(request)) {
    return finish(loadAsFile(request) ?? loadAsDirectory(request), request, fromDir);
  }

  const isRelative =
    request === '.' ||
    request === '..' ||
    request.startsWith('./') ||
    request.startsWith('../');

  if (isRelative) {
    const target = path.resolve(fromDir, request);
    return finish(loadAsFile(target) ?? loadAsDirectory(target), request, fromDir);
  }

  return finish(loadNodeModules(request, fromDir), request, fromDir);
}

export class Resolver {
  constructor(options = {}) {
    this.basedir = options.basedir ? path.resolve(options.basedir) : process.cwd();
  }

  resolve(request) {
    return resolve(request, { basedir: this.basedir });
  }
}

export default resolve;

'use strict';

const fs = require('fs');
const path = require('path');

const EXTENSIONS = ['.js', '.json', '.node'];

class ResolveError extends Error {
  constructor(request, fromDir) {
    super(`Cannot find module '${request}' from '${fromDir}'`);
    this.code = 'MODULE_NOT_FOUND';
    this.request = request;
  }
}

function isFile(file) {
  try {
    return fs.statSync(file).isFile();
  } catch {
    return false;
  }
}

function isDirectory(dir) {
  try {
    return fs.statSync(dir).isDirectory();
  } catch {
    return false;
  }
}

function readPackageMain(dir) {
  const pkgPath = path.join(dir, 'package.json');
  if (!isFile(pkgPath)) return undefined;
  try {
    const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
    return typeof pkg.main === 'string' ? pkg.main : undefined;
  } catch {
    return undefined;
  }
}

// LOAD_AS_FILE(X)
function loadAsFile(file) {
  if (isFile(file)) return file;
  for (const ext of EXTENSIONS) {
    if (isFile(file + ext)) return file + ext;
  }
  return undefined;
}

// LOAD_INDEX(X)
function loadIndex(dir) {
  for (const ext of EXTENSIONS) {
    const indexFile = path.join(dir, 'index' + ext);
    if (isFile(indexFile)) return indexFile;
  }
  return undefined;
}

// LOAD_AS_DIRECTORY(X)
function loadAsDirectory(dir) {
  const main = readPackageMain(dir);
  if (main !== undefined) {
    const mainPath = path.resolve(dir, main);
    const asFile = loadAsFile(mainPath);
    if (asFile) return asFile;
    const asIndex = loadIndex(mainPath);
    if (asIndex) return asIndex;
  }
  return loadIndex(dir);
}

// NODE_MODULES_PATHS(START)
function nodeModulesPaths(start) {
  const parts = start.split(path.sep);
  const dirs = [];
  for (let i = parts.length - 1; i >= 0; i--) {
    if (parts[i] === 'node_modules') continue;
    const dir = path.join(parts.slice(0, i + 1).join(path.sep) || path.sep, 'node_modules');
    dirs.push(dir);
  }
  return dirs;
}

// LOAD_NODE_MODULES(X, START)
function loadNodeModules(request, start) {
  for (const dir of nodeModulesPaths(start)) {
    if (!isDirectory(dir)) continue;
    const target = path.join(dir, request);
    const asFile = loadAsFile(target);
    if (asFile) return asFile;
    const asDir = loadAsDirectory(target);
    if (asDir) return asDir;
  }
  return undefined;
}

function isRelativeOrAbsolute(request) {
  return request === '.' || request === '..' ||
    request.startsWith('./') || request.startsWith('../') ||
    path.isAbsolute(request);
}

/**
 * Resolve `request` as Node's CommonJS algorithm would from a module
 * located at `fromFile` (a file path, matching require.resolve semantics).
 */
function resolve(request, fromFile) {
  const fromDir = path.dirname(path.resolve(fromFile));

  if (isRelativeOrAbsolute(request)) {
    const target = path.resolve(fromDir, request);
    const asFile = loadAsFile(target);
    if (asFile) return asFile;
    const asDir = loadAsDirectory(target);
    if (asDir) return asDir;
    throw new ResolveError(request, fromDir);
  }

  const resolved = loadNodeModules(request, fromDir);
  if (resolved) return resolved;
  throw new ResolveError(request, fromDir);
}

module.exports = { resolve, ResolveError };

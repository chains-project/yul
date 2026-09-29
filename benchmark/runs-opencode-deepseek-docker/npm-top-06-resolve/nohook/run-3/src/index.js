'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { createRequire, isBuiltin } = require('node:module');
const { pathToFileURL } = require('node:url');

/**
 * Normalize a file or directory into an absolute *file* path that can anchor a
 * `require` created with `module.createRequire`. createRequire uses the
 * dirname of its argument, so a directory must be given a synthetic child.
 */
function anchorFile(from) {
  const abs = path.resolve(from);

  let stats;
  try {
    stats = fs.statSync(abs);
  } catch {
    stats = null;
  }

  if (stats && stats.isFile()) return abs;
  if (stats && stats.isDirectory()) return path.join(abs, 'index.js');
  if (/[\\/]$/.test(from) || from === '.') return path.join(abs, 'index.js');
  return abs;
}

function requireFrom(from) {
  return createRequire(pathToFileURL(anchorFile(from)));
}

/**
 * Resolve a specifier exactly the way CommonJS `require.resolve` would, but
 * anchored at an arbitrary file or directory instead of the calling module.
 *
 * Builtins are returned unchanged (e.g. `fs`, `node:path`).
 *
 * @param {string} request Module specifier, relative path, or absolute path.
 * @param {string} [from=process.cwd()] File or directory to resolve from.
 * @returns {string} Absolute filesystem path, or the builtin id.
 */
function resolve(request, from = process.cwd()) {
  if (typeof request !== 'string' || request.length === 0) {
    throw new TypeError('request must be a non-empty string');
  }
  if (isBuiltin(request)) return request;
  return requireFrom(from).resolve(request);
}

/**
 * Every `node_modules` directory Node would search for a package, in order.
 * Mirrors `require.resolve.paths`; returns null for builtins.
 *
 * @param {string} request Module specifier.
 * @param {string} [from=process.cwd()] File or directory to resolve from.
 * @returns {string[]|null}
 */
function resolvePaths(request, from = process.cwd()) {
  if (isBuiltin(request)) return null;
  return requireFrom(from).resolve.paths(request);
}

/**
 * Resolve `request` from each anchor in order, returning the first hit.
 *
 * @param {string} request Module specifier.
 * @param {string|string[]} froms One or more anchor files/directories.
 * @returns {string}
 */
function resolveMany(request, froms) {
  const anchors = Array.isArray(froms) ? froms : [froms];
  let lastError;
  for (const from of anchors) {
    try {
      return resolve(request, from);
    } catch (error) {
      if (error.code !== 'MODULE_NOT_FOUND') throw error;
      lastError = error;
    }
  }
  if (lastError) throw lastError;
  throw new TypeError('resolveMany requires at least one anchor');
}

module.exports = { resolve, resolvePaths, resolveMany };

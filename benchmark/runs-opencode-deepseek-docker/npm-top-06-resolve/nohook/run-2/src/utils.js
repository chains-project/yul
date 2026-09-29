import fs from 'node:fs';
import path from 'node:path';
import { builtinModules } from 'node:module';

const CORE_MODULES = new Set();
for (const name of builtinModules) {
  CORE_MODULES.add(name);
  CORE_MODULES.add(`node:${name}`);
}

export function isCoreModule(specifier) {
  return CORE_MODULES.has(specifier);
}

export function isFile(candidate) {
  try {
    return fs.statSync(candidate).isFile();
  } catch {
    return false;
  }
}

export function isDirectory(candidate) {
  try {
    return fs.statSync(candidate).isDirectory();
  } catch {
    return false;
  }
}

export function nodeModulesPaths(start) {
  const absolute = path.resolve(start);
  const { root } = path.parse(absolute);
  const parts = absolute
    .slice(root.length)
    .split(path.sep)
    .filter(Boolean);

  const dirs = [];
  for (let i = parts.length; i >= 0; i -= 1) {
    if (parts[i - 1] === 'node_modules') continue;
    const base = path.join(root, ...parts.slice(0, i));
    dirs.push(path.join(base, 'node_modules'));
  }
  return dirs;
}

export function parsePackageSpecifier(specifier) {
  const parts = specifier.split('/');
  if (specifier.startsWith('@')) {
    if (parts.length < 2 || !parts[0] || !parts[1]) {
      return { packageName: null, subpath: '' };
    }
    return {
      packageName: `${parts[0]}/${parts[1]}`,
      subpath: parts.slice(2).join('/'),
    };
  }
  if (!parts[0]) {
    return { packageName: null, subpath: '' };
  }
  return { packageName: parts[0], subpath: parts.slice(1).join('/') };
}

export function isPathInside(parent, child) {
  const relative = path.relative(parent, child);
  return relative === '' || (!relative.startsWith('..') && !path.isAbsolute(relative));
}

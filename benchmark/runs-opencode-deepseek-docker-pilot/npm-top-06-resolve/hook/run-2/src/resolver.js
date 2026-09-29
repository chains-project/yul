import fs from 'node:fs'
import path from 'node:path'
import { builtinModules } from 'node:module'

const DEFAULT_EXTENSIONS = ['.js', '.json', '.node']

const BUILTINS = new Set([
  ...builtinModules,
  ...builtinModules.map((name) => `node:${name}`),
])

export class ResolveError extends Error {
  constructor(request, from) {
    super(`Cannot find module '${request}' from '${from}'`)
    this.name = 'ResolveError'
    this.code = 'MODULE_NOT_FOUND'
    this.request = request
    this.from = from
  }
}

export function isBuiltin(request) {
  if (typeof request !== 'string') return false
  return BUILTINS.has(request) || BUILTINS.has(request.replace(/^node:/, ''))
}

/**
 * Resolve a module specifier the way Node's CommonJS resolver would.
 *
 * @param {string} request - the specifier, e.g. 'foo', './bar', '#internal'.
 * @param {object} [options]
 * @param {string} [options.from] - absolute path of the importing module.
 * @param {string} [options.basedir] - directory used when `from` is omitted.
 * @param {string[]} [options.extensions] - extensions to probe.
 * @param {string[]} [options.conditions] - export conditions, default ['node', 'require'].
 * @param {boolean} [options.preserveSymlinks] - skip realpath resolution.
 * @returns {string} the resolved absolute path (or the specifier for builtins).
 */
export function resolve(request, options = {}) {
  if (typeof request !== 'string' || request.length === 0) {
    throw new TypeError('request must be a non-empty string')
  }

  const basedir = options.basedir ? path.resolve(options.basedir) : process.cwd()
  const from = options.from ? path.resolve(options.from) : path.join(basedir, 'index.js')
  const extensions = options.extensions ?? DEFAULT_EXTENSIONS
  const conditions = options.conditions ?? ['node', 'require']
  const preserveSymlinks = options.preserveSymlinks ?? false

  const done = (found) =>
    found === null ? null : preserveSymlinks ? found : finalize(found)

  if (isBuiltin(request)) return request

  if (isRelativeOrAbsolute(request)) {
    const base = path.isAbsolute(request) ? request : path.resolve(path.dirname(from), request)
    const found = done(loadAsFileOrDirectory(base, extensions))
    if (found) return found
    throw new ResolveError(request, from)
  }

  const start = isDirectory(from) ? from : path.dirname(from)

  if (request.startsWith('#')) {
    const found = done(loadPackageImports(request, start, conditions, extensions))
    if (found) return found
    throw new ResolveError(request, from)
  }

  const self = done(loadPackageSelf(request, start, conditions, extensions))
  if (self) return self

  const found = done(loadNodeModules(request, start, conditions, extensions))
  if (found) return found

  throw new ResolveError(request, from)
}

function finalize(found) {
  try {
    return fs.realpathSync(found)
  } catch {
    return found
  }
}

function isRelativeOrAbsolute(request) {
  return (
    request === '.' ||
    request === '..' ||
    request.startsWith('./') ||
    request.startsWith('../') ||
    path.isAbsolute(request)
  )
}

function isFile(candidate) {
  try {
    return fs.statSync(candidate).isFile()
  } catch {
    return false
  }
}

function isDirectory(candidate) {
  try {
    return fs.statSync(candidate).isDirectory()
  } catch {
    return false
  }
}

function readPackage(pkgPath) {
  try {
    return JSON.parse(fs.readFileSync(pkgPath, 'utf8'))
  } catch {
    return null
  }
}

function loadAsFile(base, extensions) {
  if (isFile(base)) return base
  for (const ext of extensions) {
    const candidate = `${base}${ext}`
    if (isFile(candidate)) return candidate
  }
  return null
}

function loadIndex(dir, extensions) {
  for (const ext of extensions) {
    const candidate = path.join(dir, `index${ext}`)
    if (isFile(candidate)) return candidate
  }
  return null
}

function loadAsDirectory(dir, extensions) {
  const pkgPath = path.join(dir, 'package.json')
  if (isFile(pkgPath)) {
    const pkg = readPackage(pkgPath)
    if (pkg && typeof pkg.main === 'string' && pkg.main.length > 0) {
      const mainTarget = path.resolve(dir, pkg.main)
      const asFile = loadAsFile(mainTarget, extensions)
      if (asFile) return asFile
      const asIndex = loadIndex(mainTarget, extensions)
      if (asIndex) return asIndex
    }
  }
  return loadIndex(dir, extensions)
}

function loadAsFileOrDirectory(base, extensions) {
  return loadAsFile(base, extensions) ?? loadAsDirectory(base, extensions)
}

function nodeModulesPaths(start) {
  const dirs = []
  let dir = path.resolve(start)
  for (;;) {
    if (path.basename(dir) !== 'node_modules') {
      dirs.push(path.join(dir, 'node_modules'))
    }
    const parent = path.dirname(dir)
    if (parent === dir) break
    dir = parent
  }
  return dirs
}

function loadNodeModules(request, start, conditions, extensions) {
  for (const dir of nodeModulesPaths(start)) {
    const viaExports = loadPackageExports(request, dir, conditions, extensions)
    if (viaExports) return viaExports
    const found = loadAsFileOrDirectory(path.join(dir, request), extensions)
    if (found) return found
  }
  return null
}

function parsePackageName(request) {
  const parts = request.split('/')
  if (request.startsWith('@')) {
    if (parts.length < 2) return null
    return { name: `${parts[0]}/${parts[1]}`, subpath: parts.slice(2).join('/') }
  }
  return { name: parts[0], subpath: parts.slice(1).join('/') }
}

function loadPackageExports(request, dir, conditions, extensions) {
  if (request.startsWith('.') || path.isAbsolute(request)) return null
  const parsed = parsePackageName(request)
  if (!parsed) return null

  const pkgDir = path.join(dir, parsed.name)
  const pkgPath = path.join(pkgDir, 'package.json')
  if (!isFile(pkgPath)) return null

  const pkg = readPackage(pkgPath)
  if (!pkg || pkg.exports == null) return null

  const key = parsed.subpath ? `./${parsed.subpath}` : '.'
  const target = resolveExports(pkg.exports, key, conditions)
  if (!target) return null

  return loadAsFileOrDirectory(path.resolve(pkgDir, target), extensions)
}

function loadPackageSelf(request, start, conditions, extensions) {
  const parsed = parsePackageName(request)
  if (!parsed) return null

  const pkgPath = findPackageJson(start)
  if (!pkgPath) return null

  const pkg = readPackage(pkgPath)
  if (!pkg || pkg.name !== parsed.name || pkg.exports == null) return null

  const key = parsed.subpath ? `./${parsed.subpath}` : '.'
  const target = resolveExports(pkg.exports, key, conditions)
  if (!target) return null

  return loadAsFileOrDirectory(path.resolve(path.dirname(pkgPath), target), extensions)
}

function loadPackageImports(request, start, conditions, extensions) {
  const pkgPath = findPackageJson(start)
  if (!pkgPath) return null

  const pkg = readPackage(pkgPath)
  if (!pkg || pkg.imports == null) return null

  const target = resolveExports(pkg.imports, request, conditions)
  if (!target) return null

  return loadAsFileOrDirectory(path.resolve(path.dirname(pkgPath), target), extensions)
}

function findPackageJson(start) {
  let dir = path.resolve(start)
  for (;;) {
    const candidate = path.join(dir, 'package.json')
    if (isFile(candidate)) return candidate
    const parent = path.dirname(dir)
    if (parent === dir) return null
    dir = parent
  }
}

function hasOwn(target, key) {
  return Object.prototype.hasOwnProperty.call(target, key)
}

function resolvePackageTarget(target, conditions) {
  if (target == null) return null

  if (typeof target === 'string') return target

  if (Array.isArray(target)) {
    for (const entry of target) {
      const resolved = resolvePackageTarget(entry, conditions)
      if (resolved) return resolved
    }
    return null
  }

  if (typeof target === 'object') {
    for (const condition of conditions) {
      if (hasOwn(target, condition)) {
        const resolved = resolvePackageTarget(target[condition], conditions)
        if (resolved) return resolved
      }
    }
    if (hasOwn(target, 'default')) {
      return resolvePackageTarget(target.default, conditions)
    }
  }

  return null
}

function resolveExports(exportsField, key, conditions) {
  if (exportsField == null) return null

  const isObject = typeof exportsField === 'object' && !Array.isArray(exportsField)
  const keys = isObject ? Object.keys(exportsField) : []
  const hasSubpaths = keys.some(
    (k) => k === '.' || k.startsWith('./') || k.startsWith('#'),
  )

  if (!hasSubpaths) {
    return key === '.' ? resolvePackageTarget(exportsField, conditions) : null
  }

  if (hasOwn(exportsField, key)) {
    return resolvePackageTarget(exportsField[key], conditions)
  }

  const patterns = keys
    .filter((k) => k.includes('*'))
    .sort((a, b) => b.indexOf('*') - a.indexOf('*'))

  for (const pattern of patterns) {
    const star = pattern.indexOf('*')
    const prefix = pattern.slice(0, star)
    const suffix = pattern.slice(star + 1)
    if (!key.startsWith(prefix) || !key.endsWith(suffix)) continue
    if (key.length < prefix.length + suffix.length) continue

    const matched = key.slice(prefix.length, key.length - suffix.length)
    const target = resolvePackageTarget(exportsField[pattern], conditions)
    if (target) return target.split('*').join(matched)
  }

  return null
}

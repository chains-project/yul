import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import Module, { createRequire } from 'node:module';
import { createResolver, nodeModulesPaths, resolve } from '../src/index.js';

/** Write a tree of files; object values are JSON-encoded. */
function writeTree(root, tree) {
  for (const [rel, content] of Object.entries(tree)) {
    const file = path.join(root, rel);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, typeof content === 'string' ? content : JSON.stringify(content));
  }
}

const fixture = {
  'package.json': {
    name: 'app',
    exports: { '.': './main.js', './feature': './lib/feature.js' },
    imports: {
      '#util': './lib/util.js',
      '#cond': { node: './lib/node.js', default: './lib/browser.js' },
      '#internal/*': './lib/internal/*.js',
      '#dep': 'dep-main',
      '#fs': 'fs',
      '#missing': './lib/missing.js',
      '#null': null,
    },
  },
  'main.js': '',
  'lib/feature.js': '',
  'lib/util.js': '',
  'lib/node.js': '',
  'lib/browser.js': '',
  'lib/internal/a.js': '',
  'lib/internal/deep/b.js': '',

  'src/entry.js': '',
  'src/foo.js': '',
  'src/foo.json': '{}',
  'src/data.json': '{}',
  'src/addon.node': '',
  'src/exact.txt': '',
  'src/bar/index.js': '',
  'src/bar/index.json': '{}',
  'src/jsononly/index.json': '{}',
  'src/both.js': '',
  'src/both/index.js': '',
  'src/withmain/package.json': { main: 'lib/x' },
  'src/withmain/lib/x.js': '',
  'src/maindir/package.json': { main: './lib' },
  'src/maindir/lib/index.js': '',
  'src/fallback/package.json': { main: 'nope.js' },
  'src/fallback/index.js': '',
  'src/brokenmain/package.json': { main: 'nope.js' },
  'src/brokenmain/other.js': '',
  'src/emptymain/package.json': { main: '' },
  'src/emptymain/index.js': '',
  'src/nested/deep/file.js': '',
  'src/nested/node_modules/dep-main/index.js': '',

  'node_modules/dep-main/package.json': { main: 'lib/entry.js' },
  'node_modules/dep-main/lib/entry.js': '',
  'node_modules/dep-main/other.js': '',
  'node_modules/dep-index/index.js': '',
  'node_modules/dep-file.js': '',
  'node_modules/dep-exports/package.json': {
    name: 'dep-exports',
    exports: {
      '.': { import: './esm.mjs', require: './cjs.js' },
      './sub/*': './dist/*.js',
      './sub/*.css': './styles/*.css',
      './sub/private/*': null,
      './package.json': './package.json',
      './missing': './nope.js',
      './arr': ['not-relative', './cjs.js'],
      './arr-null': [null],
      './outside': '../dep-main/other.js',
      './nm': './node_modules/x.js',
      './cond-none': { import: './esm.mjs' },
      './numeric': { 0: './cjs.js' },
    },
  },
  'node_modules/dep-exports/esm.mjs': '',
  'node_modules/dep-exports/cjs.js': '',
  'node_modules/dep-exports/unexported.js': '',
  'node_modules/dep-exports/dist/a.js': '',
  'node_modules/dep-exports/dist/nested/b.js': '',
  'node_modules/dep-exports/dist/private/c.js': '',
  'node_modules/dep-exports/styles/theme.css': '',
  'node_modules/dep-exports/node_modules/x.js': '',
  'node_modules/dep-sugar/package.json': { exports: './index.js' },
  'node_modules/dep-sugar/index.js': '',
  'node_modules/dep-sugar/other.js': '',
  'node_modules/dep-cond-sugar/package.json': { exports: { node: './node.js', default: './default.js' } },
  'node_modules/dep-cond-sugar/node.js': '',
  'node_modules/dep-cond-sugar/default.js': '',
  'node_modules/dep-null-exports/package.json': { exports: null, main: 'm.js' },
  'node_modules/dep-null-exports/m.js': '',
  'node_modules/dep-mixed/package.json': { exports: { '.': './a.js', require: './b.js' } },
  'node_modules/dep-mixed/a.js': '',
  'node_modules/@scope/pkg/package.json': { exports: { '.': './root.js', './x': './x.js' } },
  'node_modules/@scope/pkg/root.js': '',
  'node_modules/@scope/pkg/x.js': '',
  'node_modules/@scope/plain/index.js': '',
  'node_modules/dep-self/package.json': { name: 'dep-self', exports: { '.': './a.js', './b': './b.js' } },
  'node_modules/dep-self/a.js': '',
  'node_modules/dep-self/b.js': '',
  'node_modules/linked-target/index.js': '',

  'packages/noexports/package.json': { name: 'noexp' },
  'packages/noexports/index.js': '',
};

let root;
let entry;

before(() => {
  // realpath: os.tmpdir() may itself be a symlink (e.g. on macOS).
  root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'resolve-test-')));
  writeTree(root, fixture);
  fs.symlinkSync(path.join(root, 'node_modules/linked-target'), path.join(root, 'node_modules/linked'), 'dir');
  fs.symlinkSync(path.join(root, 'src/foo.js'), path.join(root, 'src/foo-link.js'));
  entry = path.join(root, 'src/entry.js');
});

after(() => {
  fs.rmSync(root, { recursive: true, force: true });
});

/** Run fn and return either { value } or { code }. */
function outcome(fn) {
  try {
    return { value: fn() };
  } catch (err) {
    return { code: err.code };
  }
}

/** Assert our resolver agrees with Node's require.resolve for this case. */
function assertMatchesNode(request, parent = entry) {
  const expected = outcome(() => createRequire(parent).resolve(request));
  const actual = outcome(() => resolve(request, parent));
  assert.deepEqual(actual, expected, `resolve(${JSON.stringify(request)}) from ${path.relative(root, parent)}`);
  return actual;
}

// [request, parent relative to root (default src/entry.js), expected outcome]
// The expected outcome documents intent; correctness is checked against Node.
const cases = {
  'core modules': [
    ['fs', , 'builtin'],
    ['node:fs', , 'builtin'],
    ['node:test', , 'builtin'],
    ['test', , 'MODULE_NOT_FOUND'],
    ['fs/promises', , 'builtin'],
  ],
  'relative and absolute paths': [
    ['./foo', , 'src/foo.js'],
    ['./foo.js', , 'src/foo.js'],
    ['./foo.json', , 'src/foo.json'],
    ['./data', , 'src/data.json'],
    ['./addon', , 'src/addon.node'],
    ['./exact.txt', , 'src/exact.txt'],
    ['./exact', , 'MODULE_NOT_FOUND'],
    ['./bar', , 'src/bar/index.js'],
    ['./bar/', , 'src/bar/index.js'],
    ['./jsononly', , 'src/jsononly/index.json'],
    ['./both', , 'src/both.js'],
    ['./both/', , 'src/both/index.js'],
    ['./foo/', , 'MODULE_NOT_FOUND'],
    ['../main', , 'main.js'],
    ['..', 'src/bar/index.js', 'MODULE_NOT_FOUND (no src/index.js)'],
    ['.', 'src/bar/x.js', 'src/bar/index.js'],
    ['./withmain', , 'src/withmain/lib/x.js'],
    ['./maindir', , 'src/maindir/lib/index.js'],
    ['./fallback', , 'src/fallback/index.js (deprecated)'],
    ['./brokenmain', , 'MODULE_NOT_FOUND'],
    ['./emptymain', , 'src/emptymain/index.js'],
    ['./nope', , 'MODULE_NOT_FOUND'],
    ['./foo-link', , 'src/foo.js (realpath)'],
    ['ABSOLUTE:src/foo', , 'src/foo.js'],
  ],
  'node_modules lookup': [
    ['dep-main', , 'node_modules/dep-main/lib/entry.js'],
    ['dep-main/other', , 'node_modules/dep-main/other.js'],
    ['dep-main', 'src/nested/deep/file.js', 'src/nested/node_modules/dep-main/index.js'],
    ['dep-index', , 'node_modules/dep-index/index.js'],
    ['dep-file', , 'node_modules/dep-file.js'],
    ['dep-main/', , 'node_modules/dep-main/lib/entry.js'],
    ['@scope/plain', , 'node_modules/@scope/plain/index.js'],
    ['linked', , 'node_modules/linked-target/index.js'],
    ['does-not-exist', , 'MODULE_NOT_FOUND'],
    ['dep-null-exports', , 'node_modules/dep-null-exports/m.js'],
    ['dep-main', 'node_modules/dep-index/index.js', 'node_modules/dep-main/lib/entry.js'],
  ],
  'package exports': [
    ['dep-exports', , 'cjs.js (require condition)'],
    ['dep-exports/sub/a', , 'dist/a.js'],
    ['dep-exports/sub/nested/b', , 'dist/nested/b.js'],
    ['dep-exports/sub/theme.css', , 'styles/theme.css (more specific pattern)'],
    ['dep-exports/sub/private/c', , 'ERR_PACKAGE_PATH_NOT_EXPORTED (null)'],
    ['dep-exports/package.json', , 'package.json'],
    ['dep-exports/unexported.js', , 'ERR_PACKAGE_PATH_NOT_EXPORTED'],
    ['dep-exports/missing', , 'MODULE_NOT_FOUND'],
    ['dep-exports/arr', , 'cjs.js (array fallback)'],
    ['dep-exports/arr-null', , 'ERR_PACKAGE_PATH_NOT_EXPORTED'],
    ['dep-exports/outside', , 'ERR_INVALID_PACKAGE_TARGET'],
    ['dep-exports/nm', , 'ERR_INVALID_PACKAGE_TARGET'],
    ['dep-exports/cond-none', , 'ERR_PACKAGE_PATH_NOT_EXPORTED'],
    ['dep-exports/numeric', , 'ERR_INVALID_PACKAGE_CONFIG'],
    ['dep-exports/sub/../cjs', , 'ERR_INVALID_MODULE_SPECIFIER'],
    ['dep-sugar', , 'index.js'],
    ['dep-sugar/other.js', , 'ERR_PACKAGE_PATH_NOT_EXPORTED'],
    ['dep-cond-sugar', , 'node.js'],
    ['dep-mixed', , 'ERR_INVALID_PACKAGE_CONFIG'],
    ['@scope/pkg', , 'root.js'],
    ['@scope/pkg/x', , 'x.js'],
    ['@scope/pkg/y', , 'ERR_PACKAGE_PATH_NOT_EXPORTED'],
  ],
  'self-reference': [
    ['app', , 'main.js'],
    ['app/feature', , 'lib/feature.js'],
    ['app/other', , 'ERR_PACKAGE_PATH_NOT_EXPORTED'],
    ['dep-self/b', 'node_modules/dep-self/a.js', 'node_modules/dep-self/b.js'],
    ['noexp', 'packages/noexports/index.js', 'MODULE_NOT_FOUND (no exports)'],
  ],
  'package imports': [
    ['#util', , 'lib/util.js'],
    ['#cond', , 'lib/node.js'],
    ['#internal/a', , 'lib/internal/a.js'],
    ['#internal/deep/b', , 'lib/internal/deep/b.js'],
    ['#dep', , 'node_modules/dep-main/lib/entry.js'],
    ['#missing', , 'MODULE_NOT_FOUND'],
    ['#null', , 'ERR_PACKAGE_IMPORT_NOT_DEFINED'],
    ['#undefined', , 'ERR_PACKAGE_IMPORT_NOT_DEFINED'],
    ['#', , 'ERR_INVALID_MODULE_SPECIFIER'],
    ['#util', 'packages/noexports/index.js', 'MODULE_NOT_FOUND (no imports field)'],
  ],
};

for (const [group, list] of Object.entries(cases)) {
  describe(group, () => {
    for (const [request, parent = 'src/entry.js', note] of list) {
      test(`${request} from ${parent} → ${note}`, () => {
        const req = request.startsWith('ABSOLUTE:') ? path.join(root, request.slice(9)) : request;
        assertMatchesNode(req, path.join(root, parent));
      });
    }
  });
}

// Node 22's CJS loader throws ERR_INVALID_URL_SCHEME for imports that map to
// a builtin, while its ESM loader resolves them. We follow the ESM behaviour.
test('imports mapping to a builtin resolve to the builtin', () => {
  assert.equal(resolve('#fs', entry), 'fs');
});

describe('options', () => {
  test('preserveSymlinks keeps the symlinked path', () => {
    const r = createResolver({ preserveSymlinks: true });
    assert.equal(r.resolve('linked', entry), path.join(root, 'node_modules/linked/index.js'));
    assert.equal(r.resolve('./foo-link', entry), path.join(root, 'src/foo-link.js'));
  });

  test('custom conditions select different export targets', () => {
    const r = createResolver({ conditions: ['import'] });
    assert.equal(r.resolve('dep-exports', entry), path.join(root, 'node_modules/dep-exports/esm.mjs'));
    assert.equal(r.resolve('#cond', entry), path.join(root, 'lib/browser.js'));
    assert.equal(r.resolve('dep-exports/cond-none', entry), path.join(root, 'node_modules/dep-exports/esm.mjs'));
  });

  test('custom extensions', () => {
    const r = createResolver({ extensions: ['.json', '.js'] });
    assert.equal(r.resolve('./foo', entry), path.join(root, 'src/foo.json'));
    assert.equal(r.resolve('./bar', entry), path.join(root, 'src/bar/index.json'));
  });

  test('extra global paths are searched last', () => {
    const r = createResolver({ paths: [path.join(root, 'packages')] });
    assert.equal(r.resolve('noexports', entry), path.join(root, 'packages/noexports/index.js'));
    assert.throws(() => resolve('noexports', entry), { code: 'MODULE_NOT_FOUND' });
  });

  test('custom isBuiltin', () => {
    const r = createResolver({ isBuiltin: (s) => s === 'virtual:env' });
    assert.equal(r.resolve('virtual:env', entry), 'virtual:env');
    assert.throws(() => r.resolve('fs', entry), { code: 'MODULE_NOT_FOUND' });
  });

  test('clearCache picks up package.json changes', () => {
    const r = createResolver();
    const pkg = path.join(root, 'src/withmain/package.json');
    assert.equal(r.resolve('./withmain', entry), path.join(root, 'src/withmain/lib/x.js'));
    fs.writeFileSync(pkg, JSON.stringify({ main: 'other.js' }));
    fs.writeFileSync(path.join(root, 'src/withmain/other.js'), '');
    try {
      assert.equal(r.resolve('./withmain', entry), path.join(root, 'src/withmain/lib/x.js'));
      r.clearCache();
      assert.equal(r.resolve('./withmain', entry), path.join(root, 'src/withmain/other.js'));
    } finally {
      fs.writeFileSync(pkg, JSON.stringify(fixture['src/withmain/package.json']));
    }
  });

  test('works against a virtual filesystem', () => {
    const files = new Map([
      ['/proj/src/index.js', ''],
      ['/proj/node_modules/pkg/package.json', JSON.stringify({ exports: { '.': './dist/index.js' } })],
      ['/proj/node_modules/pkg/dist/index.js', ''],
    ]);
    const isDir = (p) => [...files.keys()].some((f) => f.startsWith(p.endsWith('/') ? p : `${p}/`));
    const stats = (kind) => ({ isFile: () => kind === 'file', isDirectory: () => kind === 'dir' });
    const virtualFs = {
      statSync(p) {
        if (files.has(p)) return stats('file');
        if (isDir(p)) return stats('dir');
        return undefined;
      },
      readFileSync: (p) => files.get(p),
      realpathSync: (p) => p,
    };
    const r = createResolver({ fs: virtualFs });
    assert.equal(r.resolve('pkg', '/proj/src/index.js'), '/proj/node_modules/pkg/dist/index.js');
    assert.throws(() => r.resolve('./missing', '/proj/src/index.js'), { code: 'MODULE_NOT_FOUND' });
  });

  test('rejects non-absolute parent paths', () => {
    assert.throws(() => resolve('./foo', 'src/entry.js'), { code: 'ERR_INVALID_ARG_VALUE' });
  });
});

describe('nodeModulesPaths', () => {
  for (const dir of ['/', '/a', '/a/b/c', '/a/node_modules/b', '/a/node_modules/node_modules', '/node_modules']) {
    test(dir, () => {
      assert.deepEqual(nodeModulesPaths(dir), Module._nodeModulePaths(dir));
    });
  }
});

import { after, before, describe, test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { createResolver, nodeModulesPaths, resolve } from '../src/index.js';

const json = (value) => JSON.stringify(value, null, 2);

/** Fixture tree: keys are paths, values are file contents or { symlink }. */
const FIXTURES = {
  'project/package.json': json({
    name: 'my-app',
    exports: { '.': './src/main.js', './utils': './src/utils.js' },
    imports: {
      '#internal': './src/internal.js',
      '#lib/*': './src/lib/*.js',
      '#cond': { require: './src/cond.cjs', default: './src/cond.mjs' },
      '#dep': 'dep-main',
      '#dep-sub/*': 'dep-main/*',
      '#fs': 'node:fs',
      '#fs-bare': 'fs',
      '#missing': './src/does-not-exist.js',
    },
  }),
  'project/src/main.js': '',
  'project/src/utils.js': '',
  'project/src/internal.js': '',
  'project/src/lib/a.js': '',
  'project/src/cond.cjs': '',
  'project/src/cond.mjs': '',
  'project/src/plain.js': '',
  'project/src/both.js': '',
  'project/src/both.json': '',
  'project/src/data.json': '',
  'project/src/same.js': '',
  'project/src/same/index.js': '',
  'project/src/dir-index/index.js': '',
  'project/src/dir-index-json/index.json': '',
  'project/src/dir-main/package.json': json({ main: 'lib/entry' }),
  'project/src/dir-main/lib/entry.js': '',
  'project/src/dir-main-to-dir/package.json': json({ main: './lib' }),
  'project/src/dir-main-to-dir/lib/index.js': '',
  'project/src/dir-bad-main/package.json': json({ main: './missing.js' }),
  'project/src/dir-bad-main/index.js': '',
  'project/src/dir-bad-main-no-index/package.json': json({ main: './missing.js' }),
  'project/src/dir-bad-main-no-index/other.js': '',
  'project/src/nested/deep/file.js': '',

  // Plain CJS packages (no "exports").
  'project/node_modules/dep-main/package.json': json({ main: './lib/main.js' }),
  'project/node_modules/dep-main/lib/main.js': '',
  'project/node_modules/dep-main/lib/other.js': '',
  'project/node_modules/dep-main/extra.js': '',
  'project/node_modules/dep-index/index.js': '',
  'project/node_modules/dep-file.js': '',
  'project/node_modules/@scope/pkg/package.json': json({ main: 'main.js' }),
  'project/node_modules/@scope/pkg/main.js': '',
  'project/node_modules/@scope/pkg/sub/thing.js': '',
  'project/node_modules/shadowed/index.js': '',
  'project/src/nested/node_modules/shadowed/index.js': '',
  'project/node_modules/fs/index.js': '',
  'project/node_modules/test/index.js': '',
  'project/node_modules/dep-main/node_modules/inner/index.js': '',

  // Packages with "exports".
  'project/node_modules/exp-sugar/package.json': json({ exports: './sugar.js' }),
  'project/node_modules/exp-sugar/sugar.js': '',
  'project/node_modules/exp-sugar/hidden.js': '',
  'project/node_modules/exp-cond/package.json': json({
    exports: {
      '.': { import: './esm.mjs', 'module-sync': './sync.js', require: './cjs.js', default: './default.js' },
      './only-import': { import: './esm.mjs' },
      './nested': { node: { require: './cjs.js', default: './default.js' }, default: './default.js' },
      './default-first': { default: './default.js', require: './cjs.js' },
    },
  }),
  'project/node_modules/exp-cond/esm.mjs': '',
  'project/node_modules/exp-cond/sync.js': '',
  'project/node_modules/exp-cond/cjs.js': '',
  'project/node_modules/exp-cond/default.js': '',
  'project/node_modules/exp-patterns/package.json': json({
    exports: {
      '.': './index.js',
      './features/*': './src/features/*.js',
      './features/*.js': './src/features/*.js',
      './features/private/*': null,
      './features/special/*': './src/special/*.js',
      './deep/*/file': './src/deep/*/file.js',
      './multi/*': './src/multi/*/*.js',
      './array': ['./missing.js', './array.js'],
      './array-invalid-first': ['../outside.js', './array.js'],
      './bad-target': '../outside.js',
      './bad-segment': './node_modules/x.js',
      './not-relative': 'some-pkg',
      './missing-file': './nope.js',
      './dir': './src/',
      './package.json': './package.json',
    },
  }),
  'project/node_modules/exp-patterns/index.js': '',
  'project/node_modules/exp-patterns/array.js': '',
  'project/node_modules/exp-patterns/src/features/a.js': '',
  'project/node_modules/exp-patterns/src/features/sub/b.js': '',
  'project/node_modules/exp-patterns/src/features/private/c.js': '',
  'project/node_modules/exp-patterns/src/special/x.js': '',
  'project/node_modules/exp-patterns/src/deep/one/file.js': '',
  'project/node_modules/exp-patterns/src/multi/m/m.js': '',
  'project/node_modules/exp-mixed/package.json': json({ exports: { '.': './a.js', require: './b.js' } }),
  'project/node_modules/exp-mixed/a.js': '',
  'project/node_modules/exp-null/package.json': json({ exports: null, main: './main.js' }),
  'project/node_modules/exp-null/main.js': '',
  'project/node_modules/exp-no-main/package.json': json({ exports: { './sub': './sub.js' } }),
  'project/node_modules/exp-no-main/sub.js': '',
  'project/node_modules/@scope/exp/package.json': json({ exports: { '.': './i.js', './x': './x.js' } }),
  'project/node_modules/@scope/exp/i.js': '',
  'project/node_modules/@scope/exp/x.js': '',

  // A package nested inside node_modules must not see the project's scope.
  'project/node_modules/consumer/package.json': json({ name: 'consumer', exports: './c.js' }),
  'project/node_modules/consumer/c.js': '',
  'project/node_modules/consumer/lib/use.js': '',
  'project/node_modules/no-pkg-json/lib/x.js': '',

  // Symlinks.
  'linked-target/package.json': json({ main: 'real.js' }),
  'linked-target/real.js': '',
  'project/node_modules/linked': { symlink: '../../linked-target' },
  'project/src/link-to-plain.js': { symlink: './plain.js' },
};

let root;
let resolver;

before(() => {
  root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'node-module-resolver-')));
  for (const [rel, content] of Object.entries(FIXTURES)) {
    const file = path.join(root, rel);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    if (typeof content === 'string') fs.writeFileSync(file, content);
    else fs.symlinkSync(content.symlink, file);
  }
  resolver = createResolver();
});

after(() => {
  fs.rmSync(root, { recursive: true, force: true });
});

function outcome(fn) {
  try {
    return { result: fn() };
  } catch (err) {
    return { code: err.code ?? err.name };
  }
}

/** Resolve with both Node's require.resolve and our resolver; they must agree. */
function assertMatchesNode(request, fromDir) {
  const basedir = path.join(root, fromDir);
  const expected = outcome(() => createRequire(path.join(basedir, '__parent__.js')).resolve(request));
  const actual = outcome(() => resolver.resolve(request, basedir));
  assert.deepEqual(actual, expected, `require.resolve(${JSON.stringify(request)}) from ${fromDir}`);
  return actual;
}

const CASES = {
  'builtin modules': [
    ['project', 'fs'],
    ['project', 'node:fs'],
    ['project', 'fs/promises'],
    ['project', 'node:test'],
    ['project', 'test'],
    ['project', 'node:does-not-exist'],
  ],
  'relative and absolute paths': [
    ['project/src', './plain'],
    ['project/src', './plain.js'],
    ['project/src', './both'],
    ['project/src', './data'],
    ['project/src', './data.json'],
    ['project/src/nested/deep', '../../plain'],
    ['project/src/nested/deep', '../../../src/plain'],
    ['project/src', './missing'],
    ['project/src', './same'],
    ['project/src', './same/'],
    ['project/src/same', '.'],
    ['project/src/same', './'],
    ['project/src/nested', '..'],
    ['project/src/dir-index', '.'],
    ['project/src', './dir-index'],
    ['project/src', './dir-index-json'],
    ['project/src', './dir-main'],
    ['project/src', './dir-main-to-dir'],
    ['project/src', './dir-bad-main'],
    ['project/src', './dir-bad-main-no-index'],
    ['project/src', './plain.js/'],
    ['project/src', './link-to-plain'],
  ],
  'node_modules lookup': [
    ['project', 'dep-main'],
    ['project/src/nested/deep', 'dep-main'],
    ['project', 'dep-main/lib/other'],
    ['project', 'dep-main/extra.js'],
    ['project', 'dep-main/'],
    ['project', 'dep-index'],
    ['project', 'dep-file'],
    ['project', '@scope/pkg'],
    ['project', '@scope/pkg/sub/thing'],
    ['project/src', 'shadowed'],
    ['project/src/nested', 'shadowed'],
    ['project/src/nested/deep', 'shadowed'],
    ['project/node_modules/dep-main/lib', 'inner'],
    ['project', 'inner'],
    ['project', 'not-installed'],
    ['project', 'linked'],
    ['project/node_modules/no-pkg-json/lib', 'dep-main'],
  ],
  'package exports': [
    ['project', 'exp-sugar'],
    ['project', 'exp-sugar/hidden.js'],
    ['project', 'exp-sugar/package.json'],
    ['project', 'exp-cond'],
    ['project', 'exp-cond/only-import'],
    ['project', 'exp-cond/nested'],
    ['project', 'exp-cond/default-first'],
    ['project', 'exp-patterns'],
    ['project', 'exp-patterns/features/a'],
    ['project', 'exp-patterns/features/a.js'],
    ['project', 'exp-patterns/features/sub/b'],
    ['project', 'exp-patterns/features/private/c'],
    ['project', 'exp-patterns/features/special/x'],
    ['project', 'exp-patterns/features/../../index'],
    ['project', 'exp-patterns/features/node_modules/a'],
    ['project', 'exp-patterns/features/'],
    ['project', 'exp-patterns/deep/one/file'],
    ['project', 'exp-patterns/multi/m'],
    ['project', 'exp-patterns/array'],
    ['project', 'exp-patterns/array-invalid-first'],
    ['project', 'exp-patterns/bad-target'],
    ['project', 'exp-patterns/bad-segment'],
    ['project', 'exp-patterns/not-relative'],
    ['project', 'exp-patterns/missing-file'],
    ['project', 'exp-patterns/dir'],
    ['project', 'exp-patterns/package.json'],
    ['project', 'exp-patterns/index.js'],
    ['project', 'exp-mixed'],
    ['project', 'exp-null'],
    ['project', 'exp-no-main'],
    ['project', 'exp-no-main/sub'],
    ['project', '@scope/exp'],
    ['project', '@scope/exp/x'],
    ['project', '@scope/exp/i.js'],
  ],
  'package self-reference': [
    ['project/src', 'my-app'],
    ['project/src/nested/deep', 'my-app/utils'],
    ['project/src', 'my-app/src/plain.js'],
    ['project/node_modules/consumer/lib', 'consumer'],
    ['project/node_modules/consumer/lib', 'my-app'],
  ],
  'package imports': [
    ['project/src', '#internal'],
    ['project/src/nested/deep', '#lib/a'],
    ['project/src', '#lib/missing'],
    ['project/src', '#cond'],
    ['project/src', '#dep'],
    ['project/src', '#dep-sub/lib/other.js'],
    ['project/src', '#fs'],
    ['project/src', '#fs-bare'],
    ['project/src', '#missing'],
    ['project/src', '#undefined'],
    ['project/src', '#'],
    ['project/src', '#/foo'],
    ['project/node_modules/consumer/lib', '#internal'],
  ],
};

for (const [group, cases] of Object.entries(CASES)) {
  describe(group, () => {
    for (const [fromDir, request] of cases) {
      test(`${JSON.stringify(request)} from ${fromDir}`, () => {
        assertMatchesNode(request, fromDir);
      });
    }
  });
}

describe('options', () => {
  test('custom conditions select different export targets', () => {
    const r = createResolver({ conditions: ['import'] });
    const basedir = path.join(root, 'project');
    assert.equal(r.resolve('exp-cond', basedir), path.join(basedir, 'node_modules/exp-cond/esm.mjs'));
    assert.equal(r.resolve('exp-cond/only-import', basedir), path.join(basedir, 'node_modules/exp-cond/esm.mjs'));
  });

  test('custom extensions change probing order', () => {
    const r = createResolver({ extensions: ['.json', '.js'] });
    const basedir = path.join(root, 'project/src');
    assert.equal(r.resolve('./both', basedir), path.join(basedir, 'both.json'));
  });

  test('preserveSymlinks returns the symlinked path', () => {
    const r = createResolver({ preserveSymlinks: true });
    const basedir = path.join(root, 'project');
    assert.equal(r.resolve('linked', basedir), path.join(basedir, 'node_modules/linked/real.js'));
    assert.equal(r.resolve('./src/link-to-plain', basedir), path.join(basedir, 'src/link-to-plain.js'));
  });

  test('builtins: false resolves builtin names through node_modules', () => {
    const r = createResolver({ builtins: false });
    const basedir = path.join(root, 'project');
    assert.equal(r.resolve('fs', basedir), path.join(basedir, 'node_modules/fs/index.js'));
    assert.throws(() => r.resolve('node:fs', basedir), { code: 'MODULE_NOT_FOUND' });
  });

  test('paths are searched after the node_modules hierarchy', () => {
    const extra = path.join(root, 'project/src');
    const r = createResolver({ paths: [extra] });
    assert.equal(r.resolve('plain', root), path.join(extra, 'plain.js'));
    assert.throws(() => createResolver().resolve('plain', root), { code: 'MODULE_NOT_FOUND' });
  });

  test('clearCache picks up filesystem changes', () => {
    const r = createResolver();
    const basedir = path.join(root, 'project/src');
    assert.throws(() => r.resolve('./late', basedir), { code: 'MODULE_NOT_FOUND' });
    fs.writeFileSync(path.join(basedir, 'late.js'), '');
    assert.throws(() => r.resolve('./late', basedir), { code: 'MODULE_NOT_FOUND' }, 'stale cache');
    r.clearCache();
    assert.equal(r.resolve('./late', basedir), path.join(basedir, 'late.js'));
  });

  test('a custom (in-memory) fs can be supplied', () => {
    const files = new Map([
      ['/virtual/node_modules/pkg/package.json', json({ exports: { '.': { require: './c.js' } } })],
      ['/virtual/node_modules/pkg/c.js', ''],
      ['/virtual/app/index.js', ''],
    ]);
    const isDir = (p) => [...files.keys()].some((f) => f.startsWith(p.endsWith('/') ? p : `${p}/`));
    const enoent = (p) => Object.assign(new Error(`ENOENT: ${p}`), { code: 'ENOENT' });
    const memfs = {
      statSync(p) {
        if (files.has(p)) return { isFile: () => true, isDirectory: () => false };
        if (isDir(p)) return { isFile: () => false, isDirectory: () => true };
        throw enoent(p);
      },
      readFileSync(p) {
        if (!files.has(p)) throw enoent(p);
        return files.get(p);
      },
      realpathSync: (p) => p,
    };
    const r = createResolver({ fs: memfs });
    assert.equal(r.resolve('pkg', '/virtual/app'), '/virtual/node_modules/pkg/c.js');
    assert.equal(r.resolve('../app', '/virtual/lib'), '/virtual/app/index.js');
  });
});

describe('API', () => {
  test('resolve() one-off helper', () => {
    const basedir = path.join(root, 'project');
    assert.equal(resolve('dep-main', basedir), path.join(basedir, 'node_modules/dep-main/lib/main.js'));
  });

  test('rejects invalid arguments', () => {
    assert.throws(() => resolver.resolve('', root), { code: 'ERR_INVALID_ARG_VALUE' });
    assert.throws(() => resolver.resolve('x'), { code: 'ERR_INVALID_ARG_TYPE' });
  });

  test('nodeModulesPaths matches Node', () => {
    const from = path.join(root, 'project/node_modules/dep-main/lib');
    const expected = createRequire(path.join(from, 'x.js')).resolve.paths('anything');
    // Node appends global folders (~/.node_modules etc.); compare the hierarchy part.
    assert.deepEqual(nodeModulesPaths(from), expected.slice(0, nodeModulesPaths(from).length));
  });

  test('errors carry Node-style codes', () => {
    const basedir = path.join(root, 'project');
    assert.throws(() => resolver.resolve('exp-sugar/hidden.js', basedir), { code: 'ERR_PACKAGE_PATH_NOT_EXPORTED' });
    assert.throws(() => resolver.resolve('#undefined', path.join(basedir, 'src')), { code: 'ERR_PACKAGE_IMPORT_NOT_DEFINED' });
    assert.throws(() => resolver.resolve('nope', basedir), { code: 'MODULE_NOT_FOUND' });
  });
});

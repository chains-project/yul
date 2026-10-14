import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import os from 'node:os';
import path from 'node:path';
import { after, before, describe, test } from 'node:test';
import { createResolver, nodeModulesPaths, parsePackageName } from '../src/index.js';

/**
 * Writes a tree of files. String values are file contents, objects are
 * JSON-serialised (for package.json), `{ symlink }` creates a symlink.
 *
 * @param {string} root
 * @param {Record<string, unknown>} files
 */
function writeTree(root, files) {
  for (const [rel, content] of Object.entries(files)) {
    const file = path.join(root, rel);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    if (content && typeof content === 'object' && 'symlink' in content) {
      fs.symlinkSync(/** @type {string} */ (content.symlink), file, 'dir');
    } else {
      fs.writeFileSync(file, typeof content === 'string' ? content : JSON.stringify(content));
    }
  }
}

const FIXTURE = {
  'node_modules/outer/index.js': '',
  'linked-target/package.json': { name: 'linked', main: 'main.js' },
  'linked-target/main.js': '',

  'app/package.json': {
    name: 'app',
    exports: { '.': './main.js', './feature': './lib/feature.js' },
    imports: {
      '#util': './lib/util.js',
      '#dep': 'dep-exports/sub',
      '#internal/*': './lib/internal/*.js',
      '#cond': { import: './lib/esm.mjs', require: './lib/util.js' },
    },
  },
  'app/main.js': '',
  'app/lib/feature.js': '',
  'app/lib/util.js': '',
  'app/lib/esm.mjs': '',
  'app/lib/internal/a.js': '',

  'app/src/index.js': '',
  'app/src/foo.js': '',
  'app/src/foo.json': '{}',
  'app/src/data.json': '{}',
  'app/src/noext': '',
  'app/src/dir/index.json': '{}',
  'app/src/withmain/package.json': { main: './entry' },
  'app/src/withmain/entry.js': '',
  'app/src/maindir/package.json': { main: 'lib' },
  'app/src/maindir/lib/index.js': '',
  'app/src/badmain/package.json': { main: 'missing' },
  'app/src/badmain/index.js': '',
  'app/src/brokenmain/package.json': { main: 'missing' },

  'app/node_modules/plain/index.js': '',
  'app/node_modules/plain/sub.js': '',
  'app/node_modules/withmain/package.json': { main: 'lib/m' },
  'app/node_modules/withmain/lib/m.js': '',
  'app/node_modules/dep-exports/package.json': {
    exports: {
      '.': { import: './esm.mjs', require: './cjs.js' },
      './sub': './sub.js',
      './feat/*': './features/*.js',
      './feat/private/*': null,
      './package.json': './package.json',
    },
  },
  'app/node_modules/dep-exports/esm.mjs': '',
  'app/node_modules/dep-exports/cjs.js': '',
  'app/node_modules/dep-exports/sub.js': '',
  'app/node_modules/dep-exports/features/one.js': '',
  'app/node_modules/dep-exports/features/private/x.js': '',
  'app/node_modules/sugar/package.json': { exports: './s.js' },
  'app/node_modules/sugar/s.js': '',
  'app/node_modules/arr/package.json': { exports: { '.': ['not-relative', './a.js'] } },
  'app/node_modules/arr/a.js': '',
  'app/node_modules/@scope/pkg/package.json': { exports: { './x': './x.js' } },
  'app/node_modules/@scope/pkg/x.js': '',
  'app/node_modules/noext-target/package.json': { exports: './file' },
  'app/node_modules/noext-target/file.js': '',
  'app/node_modules/escape/package.json': { exports: { './x': './../../main.js' } },
  'app/node_modules/mixed/package.json': { exports: { '.': './a.js', require: './b.js' } },
  'app/node_modules/mixed/a.js': '',
  'app/node_modules/sync/package.json': {
    exports: { 'module-sync': './sync.mjs', default: './fallback.js' },
  },
  'app/node_modules/sync/sync.mjs': '',
  'app/node_modules/sync/fallback.js': '',
  'app/node_modules/linked': { symlink: '../../linked-target' },

  'app/node_modules/nested/index.js': '',
  'app/node_modules/nested/node_modules/inner/index.js': '',
};

// [request, importing file relative to the fixture root]
const CASES = [
  ['fs', 'app/src/index.js'],
  ['node:fs', 'app/src/index.js'],
  ['node:test', 'app/src/index.js'],
  ['./foo', 'app/src/index.js'],
  ['./foo.js', 'app/src/index.js'],
  ['./foo.json', 'app/src/index.js'],
  ['./data', 'app/src/index.js'],
  ['./noext', 'app/src/index.js'],
  ['./dir', 'app/src/index.js'],
  ['./dir/', 'app/src/index.js'],
  ['./withmain', 'app/src/index.js'],
  ['./maindir', 'app/src/index.js'],
  ['./badmain', 'app/src/index.js'],
  ['./brokenmain', 'app/src/index.js'],
  ['./missing', 'app/src/index.js'],
  ['../main', 'app/src/index.js'],
  ['..', 'app/src/lib-like/x.js'],
  ['.', 'app/src/dir/x.js'],
  ['plain', 'app/src/index.js'],
  ['plain/sub', 'app/src/index.js'],
  ['plain/sub.js', 'app/src/index.js'],
  ['plain/', 'app/src/index.js'],
  ['withmain', 'app/src/index.js'],
  ['dep-exports', 'app/src/index.js'],
  ['dep-exports/sub', 'app/src/index.js'],
  ['dep-exports/sub.js', 'app/src/index.js'],
  ['dep-exports/feat/one', 'app/src/index.js'],
  ['dep-exports/feat/private/x', 'app/src/index.js'],
  ['dep-exports/feat/../sub', 'app/src/index.js'],
  ['dep-exports/package.json', 'app/src/index.js'],
  ['sugar', 'app/src/index.js'],
  ['arr', 'app/src/index.js'],
  ['@scope/pkg/x', 'app/src/index.js'],
  ['@scope/pkg', 'app/src/index.js'],
  ['noext-target', 'app/src/index.js'],
  ['escape/x', 'app/src/index.js'],
  ['mixed', 'app/src/index.js'],
  ['sync', 'app/src/index.js'],
  ['linked', 'app/src/index.js'],
  ['outer', 'app/src/index.js'],
  ['nonexistent', 'app/src/index.js'],
  ['inner', 'app/node_modules/nested/index.js'],
  ['inner', 'app/src/index.js'],
  ['app', 'app/src/index.js'],
  ['app/feature', 'app/src/index.js'],
  ['app/nope', 'app/src/index.js'],
  ['#util', 'app/src/index.js'],
  ['#dep', 'app/src/index.js'],
  ['#internal/a', 'app/src/index.js'],
  ['#internal/missing', 'app/src/index.js'],
  ['#cond', 'app/src/index.js'],
  ['#nope', 'app/src/index.js'],
  ['#', 'app/src/index.js'],
];

describe('matches require.resolve', () => {
  /** @type {string} */
  let root;

  before(() => {
    // realpath: on macOS os.tmpdir() is itself behind a symlink.
    root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'resolve-fixture-')));
    writeTree(root, FIXTURE);
  });

  after(() => fs.rmSync(root, { recursive: true, force: true }));

  for (const [request, fromRel] of CASES) {
    test(`require(${JSON.stringify(request)}) from ${fromRel}`, () => {
      const from = path.join(root, fromRel);
      const expected = outcome(() => createRequire(from).resolve(request));
      const actual = outcome(() => {
        const r = createResolver().resolve(request, from);
        return r.id;
      });
      assert.deepEqual(actual, expected);
    });
  }

  test('absolute request', () => {
    const from = path.join(root, 'app/src/index.js');
    const target = path.join(root, 'app/main');
    assert.equal(createResolver().resolve(target, from).id, createRequire(from).resolve(target));
  });

  test('preserveSymlinks keeps the symlinked path', () => {
    const from = path.join(root, 'app/src/index.js');
    const { id } = createResolver({ preserveSymlinks: true }).resolve('linked', from);
    assert.equal(id, path.join(root, 'app/node_modules/linked/main.js'));
  });

  test('custom conditions', () => {
    const from = path.join(root, 'app/src/index.js');
    const { id } = createResolver({ conditions: ['import'] }).resolve('dep-exports', from);
    assert.equal(id, path.join(root, 'app/node_modules/dep-exports/esm.mjs'));
  });
});

/**
 * Normalises success/failure so results can be compared structurally.
 * @param {() => string} fn
 */
function outcome(fn) {
  try {
    return { ok: fn() };
  } catch (err) {
    return { error: /** @type {any} */ (err).code ?? String(err) };
  }
}

describe('helpers', () => {
  test('parsePackageName', () => {
    assert.deepEqual(parsePackageName('lodash'), { name: 'lodash', subpath: '' });
    assert.deepEqual(parsePackageName('lodash/fp/map'), { name: 'lodash', subpath: '/fp/map' });
    assert.deepEqual(parsePackageName('@babel/core'), { name: '@babel/core', subpath: '' });
    assert.deepEqual(parsePackageName('@babel/core/lib/x'), { name: '@babel/core', subpath: '/lib/x' });
    assert.equal(parsePackageName('.hidden'), null);
    assert.equal(parsePackageName('@scope'), null);
  });

  test('nodeModulesPaths skips node_modules directories', () => {
    const start = path.join(path.sep, 'a', 'node_modules', 'b');
    assert.deepEqual(nodeModulesPaths(start), [
      path.join(path.sep, 'a', 'node_modules', 'b', 'node_modules'),
      path.join(path.sep, 'a', 'node_modules'),
      path.join(path.sep, 'node_modules'),
    ]);
  });
});

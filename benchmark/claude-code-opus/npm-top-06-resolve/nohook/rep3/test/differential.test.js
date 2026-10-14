// Differential tests: every case is resolved both by this library and by
// Node's own createRequire(parent).resolve(), and the outcomes must match —
// same path on success, same error code on failure.

import { test, after } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { createResolver } from '../src/index.js';
import { createFixture, symlink } from './fixture.js';

const fx = createFixture({
  'package.json': {
    name: 'app',
    exports: { '.': './main.js', './feature': './lib/feature.js' },
    imports: {
      '#internal/*': './src/internal/*.js',
      '#cond': { import: './cond-import.js', require: './cond-require.js', default: './cond-default.js' },
      '#dep': 'dep-cjs',
      '#dep-sub/*': 'dep-cjs/lib/*.js',
      '#scoped': '@scope/pkg/sub/x',
      '#legacy': 'dep-legacy',
      '#missing': './nope.js',
      '#null': null,
      '#escape': '../outside.js',
    },
  },
  'main.js': '',
  'lib/feature.js': '',
  'cond-import.js': '',
  'cond-require.js': '',
  'cond-default.js': '',
  'src/index.js': '',
  'src/util.js': '',
  'src/data.json': '{}',
  'src/addon.node': '',
  'src/dir/index.js': '',
  'src/onlyjson/index.json': '{}',
  'src/both.js': '',
  'src/both/index.js': '',
  'src/withpkg/package.json': { main: './entry' },
  'src/withpkg/entry.js': '',
  'src/maindir/package.json': { main: 'lib' },
  'src/maindir/lib/index.js': '',
  'src/badmain/package.json': { main: './missing.js' },
  'src/badmain/index.js': '',
  'src/brokenmain/package.json': { main: './nope' },
  'src/internal/a.js': '',
  'src/a b.js': '',

  'node_modules/dep-cjs/package.json': { main: 'lib/index.js' },
  'node_modules/dep-cjs/lib/index.js': '',
  'node_modules/dep-cjs/lib/other.js': '',
  'node_modules/dep-cjs/node_modules/nested/index.js': '',
  'node_modules/dep-noindex/index.js': '',
  'node_modules/dep-legacy/package.json': { main: 'lib' },
  'node_modules/dep-legacy/lib/index.js': '',

  'node_modules/@scope/pkg/package.json': {
    name: '@scope/pkg',
    exports: {
      '.': { import: './esm.mjs', require: './cjs.js' },
      './sub/*': './dist/sub/*.js',
      './sub/private/*': null,
      './package.json': './package.json',
      './enc': './a%20b.js',
      './sep': './a%2Fb.js',
    },
  },
  'node_modules/@scope/pkg/cjs.js': '',
  'node_modules/@scope/pkg/esm.mjs': '',
  'node_modules/@scope/pkg/dist/sub/x.js': '',
  'node_modules/@scope/pkg/dist/sub/private/y.js': '',
  'node_modules/@scope/pkg/a b.js': '',

  'node_modules/exp-sugar/package.json': { exports: './x.js' },
  'node_modules/exp-sugar/x.js': '',
  'node_modules/exp-sugar/other.js': '',
  'node_modules/exp-array/package.json': { exports: { '.': ['not-relative', './real.js'] } },
  'node_modules/exp-array/real.js': '',
  'node_modules/exp-mixed/package.json': { exports: { '.': './a.js', b: './b.js' } },
  'node_modules/exp-numeric/package.json': { exports: { '.': { 0: './a.js' } } },
  'node_modules/exp-star/package.json': { exports: { './*': './*' } },
  'node_modules/exp-star/x.js': '',
  'node_modules/exp-nm/package.json': { exports: { './x': './node_modules/foo.js' } },
  'node_modules/exp-up/package.json': { exports: { './x': './../outside.js' } },
  'node_modules/exp-priority/package.json': {
    exports: { './*': './a/*.js', './foo/*': './b/*.js', './foo/*.js': './c/*.js' },
  },
  'node_modules/exp-priority/a/bar.js': '',
  'node_modules/exp-priority/b/bar.js': '',
  'node_modules/exp-priority/b/bar.js.js': '',
  'node_modules/exp-priority/c/bar.js': '',
  'node_modules/exp-dir/package.json': { exports: { './d': './somedir' } },
  'node_modules/exp-dir/somedir/index.js': '',
  'node_modules/exp-extless/package.json': { exports: { './x': './x' } },
  'node_modules/exp-extless/x.js': '',
  'node_modules/exp-cond/package.json': {
    exports: { import: './i.js', 'module-sync': './ms.js', node: './n.js', default: './d.js' },
  },
  'node_modules/exp-cond/i.js': '',
  'node_modules/exp-cond/ms.js': '',
  'node_modules/exp-cond/n.js': '',
  'node_modules/exp-cond/d.js': '',
  'node_modules/exp-nomain/package.json': { exports: { './a': './a.js' } },
  'node_modules/exp-nomain/a.js': '',
  'node_modules/bad-json/package.json': '{ nope',
  'node_modules/bad-json/index.js': '',
  'node_modules/linked': symlink('../packages/linked'),

  'packages/linked/package.json': { main: 'index.js' },
  'packages/linked/index.js': '',
  'packages/noimports/package.json': { name: 'noimports' },
  'packages/noimports/index.js': '',
  'packages/noimports/node_modules/#hash/index.js': '',
  'packages/self-noexports/package.json': { name: 'self-noexports' },
  'packages/self-noexports/index.js': '',
});

after(() => fx.cleanup());

const resolver = createResolver();

function outcome(fn) {
  try {
    return { path: fn() };
  } catch (err) {
    return { code: err.code ?? err.name };
  }
}

const cases = [
  // builtins
  ['src/index.js', 'fs'],
  ['src/index.js', 'node:fs'],
  ['src/index.js', 'node:test'],
  ['src/index.js', 'test'],
  ['src/index.js', 'node:does-not-exist'],

  // relative files, extensions, directories
  ['src/index.js', './util'],
  ['src/index.js', './util.js'],
  ['src/index.js', './data'],
  ['src/index.js', './addon'],
  ['src/index.js', './dir'],
  ['src/index.js', './dir/'],
  ['src/index.js', './onlyjson'],
  ['src/index.js', './both'],
  ['src/index.js', './both/'],
  ['src/index.js', './util/'],
  ['src/index.js', './withpkg'],
  ['src/index.js', './maindir'],
  ['src/index.js', './badmain'],
  ['src/index.js', './brokenmain'],
  ['src/index.js', './a b'],
  ['src/index.js', './nope'],
  ['src/dir/index.js', '.'],
  ['src/dir/index.js', '..'],
  ['src/dir/index.js', '../util'],
  ['src/index.js', '/does/not/exist'],

  // node_modules lookup
  ['src/index.js', 'dep-cjs'],
  ['src/index.js', 'dep-cjs/lib/other'],
  ['src/index.js', 'dep-cjs/'],
  ['src/index.js', 'dep-noindex'],
  ['src/index.js', 'nested'],
  ['node_modules/dep-cjs/lib/index.js', 'nested'],
  ['node_modules/dep-cjs/lib/index.js', 'dep-noindex'],
  ['src/index.js', 'linked'],
  ['src/index.js', 'bad-json'],
  ['src/index.js', 'missing-package'],
  ['src/index.js', '@scope'],

  // "exports"
  ['src/index.js', '@scope/pkg'],
  ['src/index.js', '@scope/pkg/sub/x'],
  ['src/index.js', '@scope/pkg/sub/private/y'],
  ['src/index.js', '@scope/pkg/sub/missing'],
  ['src/index.js', '@scope/pkg/package.json'],
  ['src/index.js', '@scope/pkg/cjs.js'],
  ['src/index.js', '@scope/pkg/enc'],
  ['src/index.js', '@scope/pkg/sep'],
  ['src/index.js', 'exp-sugar'],
  ['src/index.js', 'exp-sugar/other.js'],
  ['src/index.js', 'exp-array'],
  ['src/index.js', 'exp-mixed'],
  ['src/index.js', 'exp-numeric'],
  ['src/index.js', 'exp-star/x.js'],
  ['src/index.js', 'exp-star/x'],
  ['src/index.js', 'exp-star/../x.js'],
  ['src/index.js', 'exp-star/node_modules/x.js'],
  ['src/index.js', 'exp-star/a//x.js'],
  ['src/index.js', 'exp-nm/x'],
  ['src/index.js', 'exp-up/x'],
  ['src/index.js', 'exp-priority/foo/bar'],
  ['src/index.js', 'exp-priority/foo/bar.js'],
  ['src/index.js', 'exp-priority/bar'],
  ['src/index.js', 'exp-dir/d'],
  ['src/index.js', 'exp-extless/x'],
  ['src/index.js', 'exp-cond'],
  ['src/index.js', 'exp-nomain'],
  ['src/index.js', 'exp-nomain/a'],

  // self-reference
  ['src/index.js', 'app'],
  ['src/index.js', 'app/feature'],
  ['src/index.js', 'app/nope'],
  ['packages/self-noexports/index.js', 'self-noexports'],

  // "imports"
  ['src/index.js', '#internal/a'],
  ['src/index.js', '#internal/missing'],
  ['src/index.js', '#cond'],
  ['src/index.js', '#dep'],
  ['src/index.js', '#dep-sub/other'],
  ['src/index.js', '#scoped'],
  ['src/index.js', '#legacy'],
  ['src/index.js', '#missing'],
  ['src/index.js', '#null'],
  ['src/index.js', '#escape'],
  ['src/index.js', '#undefined'],
  ['src/index.js', '#'],
  ['src/index.js', '#/x'],
  ['src/index.js', '#internal/'],
  ['packages/noimports/index.js', '#hash'],
];

for (const [parent, request] of cases) {
  test(`require(${JSON.stringify(request)}) from ${parent}`, () => {
    const parentPath = fx.path(parent);
    const expected = outcome(() => createRequire(parentPath).resolve(request));
    const actual = outcome(() => resolver.resolve(request, parentPath));
    assert.deepEqual(actual, expected);
  });
}

test('createRequire-style directory parents (trailing slash)', () => {
  const dir = fx.path('src') + '/';
  assert.equal(resolver.resolve('./util', dir), createRequire(dir).resolve('./util'));
});

test('file: URL parents', () => {
  const url = new URL(`file://${fx.path('src/index.js')}`);
  assert.equal(resolver.resolve('dep-cjs', url), createRequire(url).resolve('dep-cjs'));
});

import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import path from 'node:path';
import { after, before, describe, test } from 'node:test';
import { resolve } from '../src/index.js';
import { createFixture, outcome, removeFixture, symlink } from './helpers.js';

const fixture = {
  'package.json': {
    name: 'root-pkg',
    exports: { '.': './index.js', './a': './a.js' },
    imports: {
      '#internal': './a.js',
      '#lib/*': './lib/*.js',
      '#cond': { import: './esm.mjs', require: './a.js' },
      '#dep': 'plain',
      '#dep/*': 'plain/lib/*.js',
      '#missing': './nope.js',
    },
  },
  'index.js': '',
  'a.js': '',
  'data.json': '{}',
  'noext': '',
  'foo.js': '',
  'foo': { 'index.js': '' },
  'lib': { 'util.js': '' },
  'dir-main': { 'package.json': { main: 'lib/entry' }, 'lib': { 'entry.js': '' } },
  'dir-main-dir': { 'package.json': { main: 'lib' }, 'lib': { 'index.js': '' } },
  'bad-main': { 'package.json': { main: 'missing.js' }, 'index.js': '' },
  'bad-main-noindex': { 'package.json': { main: 'missing.js' } },
  'no-imports': { 'package.json': { name: 'no-imports' }, 'index.js': '' },
  'json-index': { 'index.json': '{}' },
  'real-dir': { 'index.js': '' },
  'linked-dir': symlink('real-dir'),
  'packages': { 'linked-pkg': { 'index.js': '' } },
  'sub': {
    'deep': { 'file.js': '' },
    'node_modules': { plain: { 'package.json': { main: 'shadow.js' }, 'shadow.js': '' } },
  },
  'node_modules': {
    'plain': {
      'package.json': { main: 'main.js' },
      'main.js': '',
      'lib': { 'x.js': '' },
      'node_modules': {},
    },
    'nested-dep': { 'index.js': '' },
    '@scope': { pkg: { 'index.js': '' } },
    'linked-pkg': symlink('../packages/linked-pkg'),
    'exp-sugar': { 'package.json': { exports: './entry.js' }, 'entry.js': '', 'other.js': '' },
    'exp-cond': {
      'package.json': {
        exports: {
          '.': { import: './esm.mjs', require: './cjs.js' },
          './feature': { node: './feature-node.js', default: './feature.js' },
          './features/*': './src/features/*.js',
          './features/*.js': './src/features/*.js',
          './features/private/*': null,
          './package.json': './package.json',
        },
      },
      'esm.mjs': '',
      'cjs.js': '',
      'feature.js': '',
      'feature-node.js': '',
      'src': { features: { 'a.js': '', 'private': { 'b.js': '' } } },
    },
    'exp-array': { 'package.json': { exports: { '.': ['../escape.js', './ok.js'] } }, 'ok.js': '' },
    'exp-mixed': { 'package.json': { exports: { '.': './a.js', 'require': './b.js' } }, 'a.js': '' },
    'exp-bad-target': {
      'package.json': { exports: { './up': '../outside.js', './nm': './node_modules/z.js', './bare': 'plain' } },
    },
    'exp-missing-file': { 'package.json': { exports: './nope.js' } },
    'exp-no-ext': { 'package.json': { exports: './entry' }, 'entry.js': '' },
  },
};

let root;
before(() => {
  root = createFixture(fixture);
});
after(() => removeFixture(root));

/** Assert our resolver and Node's require.resolve agree (same path, or same error code). */
function assertMatchesNode(request, from = 'index.js') {
  const parent = path.join(root, from);
  const expected = outcome(() => createRequire(parent).resolve(request));
  const actual = outcome(() => resolve(request, parent));
  assert.deepEqual(actual, expected, `resolving ${JSON.stringify(request)} from ${from}`);
  return actual;
}

const cases = {
  'core modules': [
    ['fs'],
    ['node:fs'],
    ['node:test'],
    ['fs/promises'],
  ],
  'relative and absolute paths': [
    ['./a.js'],
    ['./a'],
    ['./data'],
    ['./noext'],
    ['./foo'],
    ['./foo/'],
    ['.'],
    ['..', 'sub/deep/file.js'],
    ['./json-index'],
    ['./missing'],
    ['../../a', 'sub/deep/file.js'],
  ],
  'package.json "main"': [
    ['./dir-main'],
    ['./dir-main-dir'],
    ['./bad-main'],
    ['./bad-main-noindex'],
  ],
  'node_modules lookup': [
    ['plain'],
    ['plain/lib/x'],
    ['plain/', 'index.js'],
    ['plain', 'sub/deep/file.js'],
    ['nested-dep', 'node_modules/plain/main.js'],
    ['@scope/pkg'],
    ['does-not-exist'],
  ],
  'package "exports"': [
    ['exp-sugar'],
    ['exp-sugar/other.js'],
    ['exp-cond'],
    ['exp-cond/feature'],
    ['exp-cond/features/a'],
    ['exp-cond/features/a.js'],
    ['exp-cond/features/private/b'],
    ['exp-cond/package.json'],
    ['exp-cond/nope'],
    ['exp-array'],
    ['exp-mixed'],
    ['exp-bad-target/up'],
    ['exp-bad-target/nm'],
    ['exp-bad-target/bare'],
    ['exp-missing-file'],
    ['exp-no-ext'],
  ],
  'package self-reference': [
    ['root-pkg', 'sub/deep/file.js'],
    ['root-pkg/a', 'sub/deep/file.js'],
    ['root-pkg/nope', 'sub/deep/file.js'],
  ],
  'package "imports"': [
    ['#internal'],
    ['#internal', 'sub/deep/file.js'],
    ['#lib/util'],
    ['#cond'],
    ['#dep'],
    ['#dep/x'],
    ['#missing'],
    ['#undefined'],
    ['#'],
    ['#internal', 'no-imports/index.js'],
  ],
  'symlinks': [
    ['./linked-dir'],
    ['linked-pkg'],
  ],
};

for (const [group, entries] of Object.entries(cases)) {
  describe(group, () => {
    for (const [request, from] of entries) {
      test(`${JSON.stringify(request)}${from ? ` from ${from}` : ''}`, () => {
        assertMatchesNode(request, from);
      });
    }
  });
}

describe('options', () => {
  test('preserveSymlinks keeps the symlinked path', () => {
    const parent = path.join(root, 'index.js');
    assert.equal(
      resolve('linked-pkg', parent, { preserveSymlinks: true }),
      path.join(root, 'node_modules/linked-pkg/index.js'),
    );
  });

  test('conditions select a different "exports" branch', () => {
    const parent = path.join(root, 'index.js');
    assert.equal(
      resolve('exp-cond', parent, { conditions: ['node', 'import'] }),
      path.join(root, 'node_modules/exp-cond/esm.mjs'),
    );
  });

  test('extensions control file probing', () => {
    const parent = path.join(root, 'index.js');
    assert.equal(
      resolve('./data', parent, { extensions: ['.json'] }),
      path.join(root, 'data.json'),
    );
    assert.throws(() => resolve('./a', parent, { extensions: ['.json'] }), { code: 'MODULE_NOT_FOUND' });
  });

  test('paths are searched after node_modules', () => {
    const parent = path.join(root, 'packages/linked-pkg/index.js');
    assert.equal(
      resolve('dir-main', parent, { paths: [root] }),
      path.join(root, 'dir-main/lib/entry.js'),
    );
  });

  test('rejects empty requests', () => {
    assert.throws(() => resolve('', path.join(root, 'index.js')), TypeError);
  });
});

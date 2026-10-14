// Behaviour driven by resolver options, which require.resolve can't be
// configured with in-process and so isn't covered by the differential suite.

import { test, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createResolver, nodeModulesPaths, patternKeyCompare } from '../src/index.js';
import { createFixture, symlink } from './fixture.js';

const fx = createFixture({
  'index.js': '',
  'util.ts': '',
  'util.js': '',
  'package.json': { imports: { '#fs': 'fs' } },
  'node_modules/cond/package.json': { exports: { browser: './browser.js', default: './default.js' } },
  'node_modules/cond/browser.js': '',
  'node_modules/cond/default.js': '',
  'node_modules/linked': symlink('../real'),
  'real/index.js': '',
  'global/lib-in-global/index.js': '',
});

after(() => fx.cleanup());

const parent = fx.path('index.js');

test('custom extensions are probed in order', () => {
  const r = createResolver({ extensions: ['.ts', '.js'] });
  assert.equal(r.resolve('./util', parent), fx.path('util.ts'));
});

test('custom conditions', () => {
  assert.equal(createResolver().resolve('cond', parent), fx.path('node_modules/cond/default.js'));
  assert.equal(
    createResolver({ conditions: ['browser', 'require'] }).resolve('cond', parent),
    fx.path('node_modules/cond/browser.js'),
  );
});

test('symlinks are realpathed unless preserveSymlinks is set', () => {
  assert.equal(createResolver().resolve('linked', parent), fx.path('real/index.js'));
  assert.equal(
    createResolver({ preserveSymlinks: true }).resolve('linked', parent),
    fx.path('node_modules/linked/index.js'),
  );
});

test('globalPaths are searched after node_modules', () => {
  assert.throws(() => createResolver().resolve('lib-in-global', parent), { code: 'MODULE_NOT_FOUND' });
  assert.equal(
    createResolver({ globalPaths: [fx.path('global')] }).resolve('lib-in-global', parent),
    fx.path('global/lib-in-global/index.js'),
  );
});

test('"imports" mapping to a builtin resolves to the node: specifier', () => {
  // Node itself throws ERR_INVALID_URL_SCHEME here; returning the builtin is
  // the useful answer for a bundler.
  assert.equal(createResolver().resolve('#fs', parent), 'node:fs');
});

test('cache is reused until clearCache()', () => {
  const r = createResolver();
  assert.throws(() => r.resolve('./late', parent), { code: 'MODULE_NOT_FOUND' });
  fs.writeFileSync(fx.path('late.js'), '');
  assert.throws(() => r.resolve('./late', parent), { code: 'MODULE_NOT_FOUND' });
  r.clearCache();
  assert.equal(r.resolve('./late', parent), fx.path('late.js'));
});

test('virtual filesystem via the fs option', () => {
  const files = new Map([
    ['/virtual/node_modules/pkg/package.json', JSON.stringify({ exports: { '.': './main.js' } })],
    ['/virtual/node_modules/pkg/main.js', ''],
  ]);
  const isDir = (p) => [...files.keys()].some((f) => f.startsWith(p + '/'));
  const vfs = {
    statSync: (p) => (files.has(p) ? { isDirectory: () => false } : isDir(p) ? { isDirectory: () => true } : undefined),
    readFileSync: (p) => files.get(p),
    realpathSync: (p) => p,
  };
  const r = createResolver({ fs: vfs });
  assert.equal(r.resolve('pkg', '/virtual/src/index.js'), '/virtual/node_modules/pkg/main.js');
});

test('rejects relative parents', () => {
  assert.throws(() => createResolver().resolve('./x', 'relative/index.js'), { code: 'ERR_INVALID_ARG_TYPE' });
});

test('nodeModulesPaths skips node_modules directories themselves', () => {
  assert.deepEqual(nodeModulesPaths('/a/node_modules/b'), [
    '/a/node_modules/b/node_modules',
    '/a/node_modules',
    '/node_modules',
  ]);
  assert.deepEqual(nodeModulesPaths('/'), ['/node_modules']);
});

test('lookupPaths', () => {
  const r = createResolver({ globalPaths: ['/g'] });
  assert.deepEqual(r.lookupPaths('./x', '/a/b/c.js'), ['/a/b']);
  assert.deepEqual(r.lookupPaths('x', '/a/b/c.js'), ['/a/b/node_modules', '/a/node_modules', '/node_modules', '/g']);
});

test('patternKeyCompare orders by specificity', () => {
  const keys = ['./*', './foo/*', './foo/*.js', './foo/bar'];
  assert.deepEqual([...keys].sort(patternKeyCompare), ['./foo/bar', './foo/*.js', './foo/*', './*']);
  assert.equal(path.sep, '/', 'path assertions above assume POSIX');
});

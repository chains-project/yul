import assert from 'node:assert/strict';
import path from 'node:path';
import { test } from 'node:test';
import { Resolver, nodeModulesPaths, patternKeyCompare } from '../src/index.js';

/** In-memory FileSystemHost: proves the resolver never touches disk itself. */
function memoryHost(files) {
  const dirs = new Set();
  for (const file of Object.keys(files)) {
    for (let d = path.dirname(file); ; d = path.dirname(d)) {
      dirs.add(d);
      if (d === path.dirname(d)) break;
    }
  }
  return {
    stat: (p) => (dirs.has(p) ? 'directory' : p in files ? 'file' : undefined),
    readFile: (p) => files[p],
    realpath: (p) => p,
  };
}

test('resolves against a virtual filesystem', () => {
  const fs = memoryHost({
    '/app/src/index.js': '',
    '/app/src/util.ts': '',
    '/app/node_modules/lib/package.json': JSON.stringify({ exports: { '.': { browser: './b.js', default: './n.js' } } }),
    '/app/node_modules/lib/b.js': '',
    '/app/node_modules/lib/n.js': '',
  });
  const resolver = new Resolver({ fs, extensions: ['.ts', '.js'], conditions: ['browser'] });

  assert.equal(resolver.resolve('./util', '/app/src/index.js'), '/app/src/util.ts');
  assert.equal(resolver.resolve('lib', '/app/src/index.js'), '/app/node_modules/lib/b.js');
  assert.throws(() => resolver.resolve('nope', '/app/src/index.js'), { code: 'MODULE_NOT_FOUND' });
});

test('caches package.json reads until clearCache()', () => {
  const files = { '/p/package.json': JSON.stringify({ main: 'a.js' }), '/p/a.js': '', '/p/b.js': '' };
  const resolver = new Resolver({ fs: memoryHost(files) });
  assert.equal(resolver.resolve('/p', '/x.js'), '/p/a.js');

  files['/p/package.json'] = JSON.stringify({ main: 'b.js' });
  assert.equal(resolver.resolve('/p', '/x.js'), '/p/a.js');
  resolver.clearCache();
  assert.equal(resolver.resolve('/p', '/x.js'), '/p/b.js');
});

test('nodeModulesPaths skips node_modules segments', () => {
  assert.deepEqual(nodeModulesPaths('/a/node_modules/b'), [
    '/a/node_modules/b/node_modules',
    '/a/node_modules',
    '/node_modules',
  ]);
});

test('patternKeyCompare orders more specific patterns first', () => {
  const keys = ['./*', './a/*', './a/*.js', './a/b'];
  assert.deepEqual(keys.sort(patternKeyCompare), ['./a/*.js', './a/*', './a/b', './*']);
});

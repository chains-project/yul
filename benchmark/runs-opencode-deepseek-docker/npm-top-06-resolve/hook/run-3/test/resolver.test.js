import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  resolve,
  resolveDetailed,
  resolveFromUrl,
  resolveSearchPaths,
} from '../src/index.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const fixtures = path.join(root, 'fixtures');

test('resolves core modules without touching the filesystem', () => {
  const fs = resolveDetailed('node:fs');
  assert.equal(fs.builtin, true);
  assert.equal(fs.url, 'node:fs');
  assert.equal(fs.path, null);

  const bare = resolveDetailed('path');
  assert.equal(bare.builtin, true);
  assert.equal(bare.url, 'node:path');
});

test('resolves relative specifiers from basedir', () => {
  const resolved = resolve('./target.js', { basedir: fixtures });
  assert.equal(resolved, path.join(fixtures, 'target.js'));
});

test('applies Node extension probing', () => {
  const resolved = resolve('./target', { basedir: fixtures });
  assert.equal(resolved, path.join(fixtures, 'target.js'));
});

test('resolves directory index files', () => {
  const resolved = resolve('./dir', { basedir: fixtures });
  assert.equal(resolved, path.join(fixtures, 'dir', 'index.js'));
});

test('resolves the package self-reference through "exports"', () => {
  const resolved = resolve('node-resolve-tool', { basedir: root });
  assert.equal(resolved, path.join(root, 'src', 'index.js'));
});

test('resolveFromUrl uses the parent module location', () => {
  const parent = new URL('../fixtures/entry.js', import.meta.url);
  const resolved = resolveFromUrl('./target.js', parent);
  assert.equal(resolved, path.join(fixtures, 'target.js'));
});

test('resolveSearchPaths returns node_modules candidates', () => {
  const paths = resolveSearchPaths('some-pkg', { basedir: path.join(fixtures, 'dir') });
  assert.ok(paths.some((p) => p.endsWith(path.join('fixtures', 'dir', 'node_modules'))));
  assert.ok(paths.some((p) => p.endsWith(path.join('fixtures', 'node_modules'))));
});

test('throws a useful error for unresolvable specifiers', () => {
  assert.throws(
    () => resolve('./does-not-exist', { basedir: fixtures }),
    /Cannot find module/,
  );
});

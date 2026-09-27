import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

import { createResolver, resolve, resolveAll } from '../src/index.js';

const dirname = path.dirname(fileURLToPath(import.meta.url));
const fixtures = path.join(dirname, '..', 'fixtures');
const consumer = path.join(fixtures, 'consumer.js');

test('resolves builtin modules with and without the node: prefix', () => {
  const plain = resolve('path');
  assert.equal(plain.isBuiltin, true);
  assert.equal(plain.resolved, 'node:path');
  assert.equal(plain.path, null);

  const prefixed = resolve('node:fs');
  assert.equal(prefixed.isBuiltin, true);
  assert.equal(prefixed.resolved, 'node:fs');
});

test('resolves relative specifiers from the anchor file', () => {
  const result = resolve('./lib.js', { from: consumer });
  assert.equal(result.path, path.join(fixtures, 'lib.js'));
  assert.equal(result.url, new URL('./lib.js', `file://${consumer}`).href);
  assert.equal(result.isRelative, true);
  assert.equal(result.isBare, false);
});

test('resolves bare specifiers through node_modules', () => {
  const result = resolve('fake-pkg', { from: consumer });
  assert.equal(result.path, path.join(fixtures, 'node_modules', 'fake-pkg', 'index.js'));
  assert.equal(result.isBare, true);
});

test('honors package exports subpaths', () => {
  const result = resolve('fake-pkg/sub', { from: consumer });
  assert.equal(
    result.path,
    path.join(fixtures, 'node_modules', 'fake-pkg', 'sub.js'),
  );
});

test('reports unresolvable specifiers with a helpful message', () => {
  assert.throws(
    () => resolve('does-not-exist-xyz', { from: consumer }),
    /Cannot resolve "does-not-exist-xyz"/,
  );
});

test('resolveAll collects successes and failures', () => {
  const results = resolveAll(['node:path', './lib.js', 'nope-xyz'], {
    from: consumer,
  });

  assert.deepEqual(
    results.map((r) => r.ok),
    [true, true, false],
  );
  assert.equal(results[0].result.resolved, 'node:path');
  assert.equal(results[1].result.path, path.join(fixtures, 'lib.js'));
  assert.ok(results[2].error instanceof Error);
});

test('createResolver binds the anchor', () => {
  const resolver = createResolver({ from: fixtures });
  assert.equal(resolver.from, fixtures);
  assert.equal(
    resolver.resolve('./lib.js').path,
    path.join(fixtures, 'lib.js'),
  );
});

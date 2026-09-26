'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { resolve, ResolveError } = require('../src/resolve');

const fixtures = path.join(__dirname, 'fixtures');
const entry = path.join(fixtures, 'entry.js');

test('resolves a relative file with an implicit .js extension', () => {
  assert.equal(resolve('./lib/foo', entry), path.join(fixtures, 'lib/foo.js'));
});

test('resolves a relative file with an implicit .json extension', () => {
  assert.equal(resolve('./lib/baz', entry), path.join(fixtures, 'lib/baz.json'));
});

test('resolves a relative directory via its index.js', () => {
  assert.equal(resolve('./lib/bar', entry), path.join(fixtures, 'lib/bar/index.js'));
});

test('resolves an exact relative file with no extension resolution needed', () => {
  assert.equal(resolve('./entry.js', entry), entry);
});

test('resolves a node_modules package via its package.json "main" field', () => {
  assert.equal(
    resolve('pkg-main', entry),
    path.join(fixtures, 'node_modules/pkg-main/lib/entry.js')
  );
});

test('resolves a node_modules package via its index.js when there is no main', () => {
  assert.equal(
    resolve('pkg-index', entry),
    path.join(fixtures, 'node_modules/pkg-index/index.js')
  );
});

test('prefers the nearest node_modules directory when walking up', () => {
  const nestedEntry = path.join(fixtures, 'node_modules/nested/index.js');
  assert.equal(
    resolve('inner', nestedEntry),
    path.join(fixtures, 'node_modules/nested/node_modules/inner/index.js')
  );
});

test('throws MODULE_NOT_FOUND for a missing relative module', () => {
  assert.throws(
    () => resolve('./does-not-exist', entry),
    (err) => err instanceof ResolveError && err.code === 'MODULE_NOT_FOUND'
  );
});

test('throws MODULE_NOT_FOUND for a missing bare specifier', () => {
  assert.throws(
    () => resolve('nonexistent-package', entry),
    (err) => err instanceof ResolveError && err.code === 'MODULE_NOT_FOUND'
  );
});

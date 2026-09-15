'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { resolveModule, resolveModuleAsync } = require('./index.js');

test('resolves a relative file with an implicit extension', () => {
  const resolved = resolveModule('./fixtures/foo', __dirname);
  assert.equal(resolved, path.join(__dirname, 'fixtures', 'foo.js'));
});

test('resolves a package directory via its main field', () => {
  const resolved = resolveModule('resolve', __dirname);
  assert.ok(resolved.endsWith(path.join('resolve', 'index.js')));
});

test('resolveModuleAsync matches resolveModule', async () => {
  const sync = resolveModule('resolve', __dirname);
  const async = await resolveModuleAsync('resolve', __dirname);
  assert.equal(async, sync);
});

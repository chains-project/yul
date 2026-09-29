'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const os = require('node:os');
const path = require('node:path');

const { resolve, resolvePaths, resolveMany } = require('../src/index.js');

const FIXTURES = path.join(__dirname, 'fixtures');
const APP = path.join(FIXTURES, 'app', 'index.js');
const APP_DIR = path.join(FIXTURES, 'app');

test('returns builtin ids untouched', () => {
  assert.equal(resolve('fs'), 'fs');
  assert.equal(resolve('node:path'), 'node:path');
});

test('resolves a relative file from a file anchor', () => {
  assert.equal(resolve('./helper', APP), path.join(APP_DIR, 'helper.js'));
});

test('resolves a relative file from a directory anchor', () => {
  assert.equal(resolve('./helper', APP_DIR), path.join(APP_DIR, 'helper.js'));
});

test('resolves a package through node_modules', () => {
  assert.equal(
    resolve('left-pad', APP),
    path.join(FIXTURES, 'node_modules', 'left-pad', 'index.js')
  );
});

test('honors a directory package.json "main" field', () => {
  assert.equal(resolve('./lib', APP), path.join(APP_DIR, 'lib', 'main.js'));
});

test('exposes the search paths Node would use', () => {
  const paths = resolvePaths('left-pad', APP);
  assert.ok(Array.isArray(paths));
  assert.ok(paths.includes(path.join(APP_DIR, 'node_modules')));
  assert.ok(paths.includes(path.join(FIXTURES, 'node_modules')));
  assert.equal(resolvePaths('fs', APP), null);
});

test('throws MODULE_NOT_FOUND with a helpful message', () => {
  assert.throws(
    () => resolve('does-not-exist-xyz', APP),
    (error) =>
      error.code === 'MODULE_NOT_FOUND' &&
      /does-not-exist-xyz/.test(error.message)
  );
});

test('resolveMany falls through to the first anchor that succeeds', () => {
  const missing = path.join(os.tmpdir(), 'nmr-missing-anchor', 'index.js');
  assert.equal(resolveMany('./helper', [missing, APP]), path.join(APP_DIR, 'helper.js'));
});

test('rejects non-string requests', () => {
  assert.throws(() => resolve(''), TypeError);
});

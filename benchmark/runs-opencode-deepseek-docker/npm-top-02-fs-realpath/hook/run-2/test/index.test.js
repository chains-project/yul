'use strict';

var assert = require('assert');
var fs = require('fs');
var os = require('os');
var path = require('path');

var canonicalPath = require('..');
var canonicalPathSync = canonicalPath.canonicalPathSync;

var root = fs.mkdtempSync(path.join(os.tmpdir(), 'canonical-path-'));
// Collapse any symlinks in the OS temp dir itself so expectations are stable.
var realRoot = fs.realpathSync(root);

var realDir = path.join(root, 'real');
var nestedDir = path.join(realDir, 'nested');
fs.mkdirSync(nestedDir, { recursive: true });
fs.writeFileSync(path.join(nestedDir, 'file.txt'), 'hello\n');

var dirLink = path.join(root, 'dir-link');
var nestedLink = path.join(root, 'nested-link');
var chainLink = path.join(root, 'chain-link');

fs.symlinkSync(realDir, dirLink);
fs.symlinkSync(path.join(realDir, 'nested'), nestedLink);
fs.symlinkSync(dirLink, chainLink);

var tests = [];
function test(name, fn) {
  tests.push([name, fn]);
}

test('resolves a symlinked file to its canonical path', function () {
  var actual = canonicalPathSync(path.join(dirLink, 'nested', 'file.txt'));
  var expected = path.join(realRoot, 'real', 'nested', 'file.txt');
  assert.strictEqual(actual, expected);
});

test('resolves a symlink in the middle of a path', function () {
  var actual = canonicalPathSync(path.join(nestedLink, 'file.txt'));
  assert.strictEqual(actual, path.join(realRoot, 'real', 'nested', 'file.txt'));
});

test('collapses a chain of symlinks', function () {
  var actual = canonicalPathSync(chainLink);
  assert.strictEqual(actual, path.join(realRoot, 'real'));
});

test('accepts a relative path', function () {
  var previous = process.cwd();
  process.chdir(root);
  try {
    assert.strictEqual(canonicalPathSync('dir-link'), path.join(realRoot, 'real'));
  } finally {
    process.chdir(previous);
  }
});

test('async form matches the sync form', function (done) {
  canonicalPath(path.join(dirLink, 'nested', 'file.txt'), function (err, resolved) {
    if (err) return done(err);
    try {
      assert.strictEqual(
        resolved,
        canonicalPathSync(path.join(dirLink, 'nested', 'file.txt'))
      );
    } catch (assertionError) {
      return done(assertionError);
    }
    done();
  });
});

test('rejects a non-string path', function () {
  assert.throws(function () {
    canonicalPathSync(42);
  }, TypeError);
});

var index = 0;

function finish(err, name) {
  if (err) {
    console.error('FAIL - ' + name);
    console.error(err && err.stack ? err.stack : err);
    process.exitCode = 1;
  } else {
    console.log('ok - ' + name);
  }
  index += 1;
  next();
}

function next() {
  if (index >= tests.length) {
    if (!process.exitCode) console.log('\n' + tests.length + ' tests passed');
    process.exit(process.exitCode || 0);
  }
  var name = tests[index][0];
  var fn = tests[index][1];
  try {
    if (fn.length > 0) {
      fn(function (err) {
        finish(err, name);
      });
    } else {
      fn();
      finish(null, name);
    }
  } catch (err) {
    finish(err, name);
  }
}
next();

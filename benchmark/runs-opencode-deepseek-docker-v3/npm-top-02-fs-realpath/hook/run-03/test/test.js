'use strict';

var assert = require('assert');
var fs = require('fs');
var os = require('os');
var path = require('path');
var realpath = require('..');

var nativeSync = typeof fs.realpathSync.native === 'function'
  ? fs.realpathSync.native
  : fs.realpathSync;

var tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'resolve-realpath-'));
var tests = [];
var failed = 0;

function test(name, fn) {
  tests.push({ name: name, fn: fn });
}

function makeSymlink(target, linkPath, type) {
  try {
    fs.symlinkSync(target, linkPath, type);
    return true;
  } catch (err) {
    if (err.code === 'EPERM' || err.code === 'EACCES' || err.code === 'ENOSYS') {
      return false;
    }
    throw err;
  }
}

var realDir = path.join(tmp, 'real-dir');
var nestedDir = path.join(realDir, 'nested');
var realFile = path.join(nestedDir, 'file.txt');
fs.mkdirSync(nestedDir, { recursive: true });
fs.writeFileSync(realFile, 'hello');

var linkDir = path.join(tmp, 'link-dir');
var linkFile = path.join(tmp, 'link-file');
var linkChain = path.join(tmp, 'link-chain');
var linkRelative = path.join(tmp, 'link-relative');

var symlinksSupported = makeSymlink(realDir, linkDir, 'dir');
symlinksSupported = makeSymlink(realFile, linkFile, 'file') && symlinksSupported;
symlinksSupported = makeSymlink(linkDir, linkChain, 'dir') && symlinksSupported;
symlinksSupported = makeSymlink(path.relative(tmp, realDir), linkRelative, 'dir') && symlinksSupported;

test('exposes sync, callback and promise APIs', function () {
  assert.strictEqual(typeof realpath, 'function');
  assert.strictEqual(typeof realpath.sync, 'function');
  assert.strictEqual(typeof realpath.realpathSync, 'function');
  assert.strictEqual(typeof realpath.promises, 'function');
});

test('resolves a plain path to its canonical form', function () {
  assert.strictEqual(realpath.sync(realFile), nativeSync(realFile));
});

test('throws ENOENT for a missing path', function () {
  assert.throws(function () {
    realpath.sync(path.join(tmp, 'does-not-exist'));
  }, function (err) {
    return err.code === 'ENOENT';
  });
});

if (symlinksSupported) {
  test('resolves a symlinked file to the real file', function () {
    assert.strictEqual(realpath.sync(linkFile), nativeSync(realFile));
  });

  test('resolves a symlinked directory to the real directory', function () {
    assert.strictEqual(realpath.sync(linkDir), nativeSync(realDir));
  });

  test('resolves a chain of symlinks to the final target', function () {
    assert.strictEqual(realpath.sync(linkChain), nativeSync(realDir));
  });

  test('resolves a relative symlink', function () {
    assert.strictEqual(realpath.sync(linkRelative), nativeSync(realDir));
  });

  test('resolves .. after a symlinked directory the same way the OS does', function () {
    var viaLink = linkDir + path.sep + '..' + path.sep + 'real-dir';
    assert.strictEqual(realpath.sync(viaLink), nativeSync(viaLink));
  });

  test('is idempotent', function () {
    var once = realpath.sync(linkDir);
    assert.strictEqual(realpath.sync(once), once);
  });
} else {
  process.stdout.write('ok - # SKIP symlink tests (not permitted on this platform)\n');
}

test('async callback API matches sync API', function (done) {
  realpath(linkFile, function (err, resolved) {
    if (err) {
      done(err);
      return;
    }
    try {
      assert.strictEqual(resolved, realpath.sync(linkFile));
      done();
    } catch (assertionErr) {
      done(assertionErr);
    }
  });
});

test('promise API matches sync API', function (done) {
  realpath.promises(linkFile).then(function (resolved) {
    try {
      assert.strictEqual(resolved, realpath.sync(linkFile));
      done();
    } catch (assertionErr) {
      done(assertionErr);
    }
  }, done);
});

test('promise API rejects for a missing path', function (done) {
  realpath.promises(path.join(tmp, 'does-not-exist')).then(function () {
    done(new Error('expected rejection'));
  }, function (err) {
    try {
      assert.strictEqual(err.code, 'ENOENT');
      done();
    } catch (assertionErr) {
      done(assertionErr);
    }
  });
});

function run(index) {
  if (index >= tests.length) {
    process.exitCode = failed ? 1 : 0;
    return;
  }

  var current = tests[index];
  var settled = false;

  function next(err) {
    if (settled) {
      return;
    }
    settled = true;
    if (err) {
      failed += 1;
      process.stderr.write('not ok - ' + current.name + '\n  ' + (err.stack || err.message || err) + '\n');
    } else {
      process.stdout.write('ok - ' + current.name + '\n');
    }
    run(index + 1);
  }

  if (current.fn.length >= 1) {
    try {
      current.fn(next);
    } catch (err) {
      next(err);
    }
  } else {
    try {
      current.fn();
      next();
    } catch (err) {
      next(err);
    }
  }
}

run(0);

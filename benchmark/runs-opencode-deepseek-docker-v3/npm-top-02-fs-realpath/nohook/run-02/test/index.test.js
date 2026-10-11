'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

const realpath = require('../index.js');

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'realpath-resolver-'));
const targetDir = path.join(tmp, 'target');
const linkPath = path.join(tmp, 'link');
const nestedLink = path.join(tmp, 'nested', 'link');

fs.mkdirSync(targetDir);
fs.mkdirSync(path.join(tmp, 'nested'));
fs.writeFileSync(path.join(targetDir, 'file.txt'), 'hello');

const linkType = process.platform === 'win32' ? 'junction' : 'dir';
fs.symlinkSync(targetDir, linkPath, linkType);
fs.symlinkSync(linkPath, nestedLink, linkType);

const expected = realpath.sync(targetDir);

assert.strictEqual(realpath.sync(linkPath), expected);
assert.strictEqual(realpath.sync(nestedLink), expected);
assert.strictEqual(realpath.sync(path.join(linkPath, 'file.txt')), path.join(expected, 'file.txt'));

assert.throws(() => realpath.sync(123), TypeError);

const viaCallback = realpath.sync(nestedLink);
assert.strictEqual(realpath.sync(nestedLink), viaCallback);

realpath(nestedLink, function (err, resolved) {
  assert.ifError(err);
  assert.strictEqual(resolved, expected);

  fs.rmSync(tmp, { recursive: true, force: true });
  process.stdout.write('ok\n');
});

'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { toRealPath } = require('./index');

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'realpath-'));
const realFile = path.join(tmp, 'real.txt');
const linkFile = path.join(tmp, 'link.txt');

fs.writeFileSync(realFile, 'hello');
fs.symlinkSync(realFile, linkFile);

try {
  assert.strictEqual(toRealPath(linkFile), fs.realpathSync(realFile));
  console.log('ok');
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}

'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { realpath } = require('./index');

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'realpath-'));
const realFile = path.join(tmp, 'real.txt');
const link = path.join(tmp, 'link.txt');
const nestedLink = path.join(tmp, 'nested.txt');

fs.writeFileSync(realFile, 'hello');
fs.symlinkSync(realFile, link);
fs.symlinkSync(link, nestedLink);

realpath(nestedLink)
  .then((resolved) => {
    assert.strictEqual(resolved, fs.realpathSync(realFile));
    assert.strictEqual(resolved, realFile);
    console.log('ok');
  })
  .catch((err) => {
    console.error(err);
    process.exit(1);
  })
  .finally(() => {
    fs.rmSync(tmp, { recursive: true, force: true });
  });

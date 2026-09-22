'use strict';

const test = require('node:test');
const assert = require('node:assert');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const { parseRange } = require('../cli.js');

const cli = path.join(__dirname, '..', 'cli.js');
const run = args => execFileSync(process.execPath, [cli, ...args], { encoding: 'utf8' }).trim();

test('parseRange parses "1-100"', () => {
  assert.deepStrictEqual(parseRange('1-100'), [1, 100]);
  assert.deepStrictEqual(parseRange(' -5-5 '), [-5, 5]);
  assert.deepStrictEqual(parseRange('10..20'), [10, 20]);
});

test('parseRange rejects invalid input', () => {
  assert.throws(() => parseRange('abc'), /invalid range/);
});

test('cli converts a range to a regex', () => {
  assert.strictEqual(run(['1-100']), '(?:[1-9]|[1-9][0-9]|100)');
  assert.strictEqual(run(['5-5']), '5');
  assert.strictEqual(run(['1-100', '--shorthand']), '(?:[1-9]|[1-9]\\d|100)');
});

'use strict';

const assert = require('assert');
const rangeToRegex = require('./index.js');

const regex = rangeToRegex('1-100');

assert.strictEqual(regex.test('1'), true);
assert.strictEqual(regex.test('50'), true);
assert.strictEqual(regex.test('100'), true);
assert.strictEqual(regex.test('0'), false);
assert.strictEqual(regex.test('101'), false);

assert.throws(() => rangeToRegex('nope'), TypeError);

console.log('All tests passed.');

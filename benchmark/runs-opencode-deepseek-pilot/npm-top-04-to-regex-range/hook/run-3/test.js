'use strict';

const assert = require('assert');
const rangeToRegex = require('./index');
const { rangeToRegExp } = require('./index');

assert.strictEqual(rangeToRegex('1-100'), '(?:[1-9]|[1-9][0-9]|100)');

const re = rangeToRegExp('1-100');
assert.ok(re.test('1'));
assert.ok(re.test('50'));
assert.ok(re.test('100'));
assert.ok(!re.test('0'));
assert.ok(!re.test('101'));
assert.ok(!re.test('1.5'));

const single = rangeToRegExp('5-5');
assert.ok(single.test('5'));
assert.ok(!single.test('4'));

const negative = rangeToRegExp('-10--1');
assert.ok(negative.test('-10'));
assert.ok(negative.test('-1'));
assert.ok(!negative.test('0'));

assert.throws(() => rangeToRegex('abc'), /Invalid numeric range/);

console.log('All tests passed');

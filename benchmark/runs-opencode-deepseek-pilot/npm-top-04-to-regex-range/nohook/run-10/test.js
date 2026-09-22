'use strict';

const assert = require('assert');
const { execFileSync } = require('child_process');
const path = require('path');
const toRegexRange = require('./');

let passed = 0;
const test = (name, fn) => {
  try {
    fn();
    passed++;
  } catch (err) {
    console.error(`not ok - ${name}`);
    throw err;
  }
};

const matches = (source, value) => new RegExp(`^(?:${source})$`).test(String(value));

test('single number', () => {
  assert.strictEqual(toRegexRange(5), '5');
});

test('equal bounds', () => {
  assert.strictEqual(toRegexRange('5', '5'), '5');
});

test('adjacent numbers', () => {
  assert.strictEqual(toRegexRange('5', '6'), '(?:5|6)');
});

test('adjacent numbers, wrap disabled', () => {
  assert.strictEqual(toRegexRange('5', '6', { wrap: false }), '5|6');
});

test('adjacent numbers, capture enabled', () => {
  assert.strictEqual(toRegexRange('5', '6', { capture: true }), '(5|6)');
});

test('range 1-100', () => {
  assert.strictEqual(toRegexRange(1, 100), '(?:[1-9]|[1-9][0-9]|100)');
});

test('range 1-100 shorthand', () => {
  assert.strictEqual(toRegexRange(1, 100, { shorthand: true }), '(?:[1-9]|[1-9]\\d|100)');
});

test('range 1-100 capture', () => {
  assert.strictEqual(toRegexRange(1, 100, { capture: true }), '([1-9]|[1-9][0-9]|100)');
});

test('range 1-100 matches members only', () => {
  let source = toRegexRange(1, 100);
  for (let i = 1; i <= 100; i++) {
    assert.ok(matches(source, i), `expected ${i} to match`);
  }
  for (let i of [0, 101, 1000]) {
    assert.ok(!matches(source, i), `expected ${i} not to match`);
  }
});

test('padded range', () => {
  assert.strictEqual(toRegexRange('001', '100'), '(?:0{0,2}[1-9]|0?[1-9][0-9]|100)');
});

test('strict zeros', () => {
  assert.strictEqual(toRegexRange('001', '100', { strictZeros: true }), '(?:00[1-9]|0[1-9][0-9]|100)');
});

test('negative to positive', () => {
  let source = toRegexRange(-10, 10);
  for (let i = -10; i <= 10; i++) {
    assert.ok(matches(source, i), `expected ${i} to match`);
  }
  assert.ok(!matches(source, -11));
  assert.ok(!matches(source, 11));
});

test('functional across many ranges', () => {
  for (let a = 0; a <= 40; a++) {
    for (let b = a; b <= 120; b++) {
      let source = toRegexRange(a, b);
      for (let n = a; n <= b; n++) {
        assert.ok(matches(source, n), `range ${a}-${b}: expected ${n} to match`);
      }
      if (a > 0) assert.ok(!matches(source, a - 1), `range ${a}-${b}: expected ${a - 1} not to match`);
      assert.ok(!matches(source, b + 1), `range ${a}-${b}: expected ${b + 1} not to match`);
    }
  }
});

test('throws on non-number', () => {
  assert.throws(() => toRegexRange('foo'), TypeError);
  assert.throws(() => toRegexRange(1, 'bar'), TypeError);
});

test('cache can be cleared', () => {
  toRegexRange(1, 100);
  assert.ok(Object.keys(toRegexRange.cache).length > 0);
  toRegexRange.clearCache();
  assert.strictEqual(Object.keys(toRegexRange.cache).length, 0);
});

test('cli converts "1-100"', () => {
  let cli = path.join(__dirname, 'bin', 'cli.js');
  let output = execFileSync(process.execPath, [cli, '1-100'], { encoding: 'utf8' }).trim();
  assert.strictEqual(output, '(?:[1-9]|[1-9][0-9]|100)');
});

test('cli accepts two numbers', () => {
  let cli = path.join(__dirname, 'bin', 'cli.js');
  let output = execFileSync(process.execPath, [cli, '1', '100'], { encoding: 'utf8' }).trim();
  assert.strictEqual(output, '(?:[1-9]|[1-9][0-9]|100)');
});

console.log(`ok - ${passed} tests passed`);

'use strict';

const assert = require('assert');
const toRegexRange = require('../');

function matches(range, n) {
  const re = new RegExp(`^(?:${toRegexRange(range[0], range[1])})$`);
  return re.test(String(n));
}

function verify(range) {
  const [min, max] = range;
  for (let n = min; n <= max; n++) {
    assert.ok(matches(range, n), `${toRegexRange(min, max)} should match ${n}`);
  }
  for (const n of [min - 1, max + 1, min - 10, max + 10]) {
    assert.ok(!matches(range, n), `${toRegexRange(min, max)} should not match ${n}`);
  }
}

const cases = [
  [0, 0],
  [1, 9],
  [1, 10],
  [1, 100],
  [0, 100],
  [12, 34],
  [10, 99],
  [100, 999],
  [123, 4567],
  [1000, 9999],
  [1, 65535],
  [-5, 5],
  [-100, -1],
  [-100, 100],
  [-50, 50],
];

for (const range of cases) {
  verify(range);
}

assert.strictEqual(toRegexRange(1, 100), '(?:[1-9]|[1-9][0-9]|100)');
assert.strictEqual(toRegexRange(1, 9), '[1-9]');
assert.strictEqual(toRegexRange(5, 5), '5');
assert.strictEqual(toRegexRange(1, 100, { anchor: true }), '^(?:[1-9]|[1-9][0-9]|100)$');
assert.strictEqual(toRegexRange(1, 9, { capture: true }), '([1-9])');
assert.throws(() => toRegexRange(1.5, 10), TypeError);

process.stdout.write('All tests passed.\n');

'use strict';

const assert = require('assert');
const toRegexRange = require('./index.js');

const matches = (source, value) => new RegExp(`^(?:${source})$`).test(String(value));

const cases = [
  [1, 100],
  [1, 10],
  [1, 5],
  [0, 9],
  [-5, 5],
  [-100, -1],
  [100, 200],
  [5, 5],
  [0, 100],
  [1, 1000],
  [12, 3456],
  [-20, 30],
  [1000, 2000]
];

for (const [min, max] of cases) {
  const source = toRegexRange(min, max);
  for (let n = min - 5; n <= max + 5; n++) {
    const expected = n >= min && n <= max;
    assert.strictEqual(
      matches(source, n),
      expected,
      `${min}-${max}: ${n} against /${source}/`
    );
  }
}

assert.strictEqual(toRegexRange(1, 100), '(?:[1-9]|[1-9][0-9]|100)');
assert.strictEqual(toRegexRange(1, 5), '[1-5]');
assert.strictEqual(toRegexRange(5, 5), '5');
assert.strictEqual(toRegexRange(0, 9), '[0-9]');

assert.throws(() => toRegexRange('a', 10), TypeError);
assert.throws(() => toRegexRange(1, 'b'), TypeError);

console.log('All tests passed.');

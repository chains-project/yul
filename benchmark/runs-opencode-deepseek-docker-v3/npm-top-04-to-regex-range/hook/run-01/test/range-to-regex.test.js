import assert from 'node:assert/strict';
import test from 'node:test';
import {
  parseRange,
  rangeToRegex,
  rangeToRegexFromString,
  toRegexSource,
} from '../src/range-to-regex.js';

test('parseRange parses and trims whitespace', () => {
  assert.deepEqual(parseRange('1-100'), { min: 1, max: 100 });
  assert.deepEqual(parseRange(' 0 - 9 '), { min: 0, max: 9 });
});

test('parseRange rejects malformed input', () => {
  assert.throws(() => parseRange('100'), SyntaxError);
  assert.throws(() => parseRange('1..100'), SyntaxError);
  assert.throws(() => parseRange(100), TypeError);
});

test('toRegexSource rejects invalid bounds', () => {
  assert.throws(() => toRegexSource(100, 1), RangeError);
  assert.throws(() => toRegexSource(-1, 10), RangeError);
  assert.throws(() => toRegexSource(1.5, 10), TypeError);
});

test('rangeToRegex returns a usable RegExp', () => {
  const re = rangeToRegexFromString('1-100');
  assert.ok(re instanceof RegExp);
  assert.ok(re.test('1'));
  assert.ok(re.test('42'));
  assert.ok(re.test('100'));
  assert.ok(!re.test('0'));
  assert.ok(!re.test('101'));
  assert.ok(!re.test('1.5'));
  assert.ok(!re.test('007'));
});

test('single-value range matches literal', () => {
  const re = rangeToRegex(7, 7);
  assert.ok(re.test('7'));
  assert.ok(!re.test('8'));
});

test('full membership matches for many small ranges', () => {
  const MAX = 120;
  for (let min = 0; min <= MAX; min += 1) {
    for (let max = min; max <= MAX; max += 1) {
      const re = rangeToRegex(min, max);
      for (let n = 0; n <= MAX + 5; n += 1) {
        const expected = n >= min && n <= max;
        assert.equal(
          re.test(String(n)),
          expected,
          `range ${min}-${max} testing ${n} (source ${re.source})`,
        );
      }
    }
  }
});

test('regex does not accept leading zeros', () => {
  const re = rangeToRegex(0, 100);
  for (const value of ['00', '01', '0100', '0000']) {
    assert.ok(!re.test(value), `should not match ${value}`);
  }
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { parseRange, rangeToRegex } from '../src/range-to-regex.js';

test('parses ranges like "1-100"', () => {
  assert.deepEqual(parseRange('1-100'), [1, 100]);
  assert.deepEqual(parseRange(' 10 - 20 '), [10, 20]);
  assert.throws(() => parseRange('nope'));
  assert.throws(() => parseRange('1-'));
});

test('matches exactly the numbers in the range', () => {
  const ranges = [
    [0, 0],
    [5, 5],
    [1, 9],
    [1, 10],
    [1, 100],
    [0, 100],
    [95, 105],
    [89, 111],
    [123, 456],
    [999, 1000],
    [1000, 1000],
    [1, 1000],
  ];

  for (const [min, max] of ranges) {
    const re = rangeToRegex(min, max);
    for (let n = Math.max(0, min - 2); n <= max + 2; n += 1) {
      const expected = n >= min && n <= max;
      assert.equal(re.test(String(n)), expected, `${min}-${max} tested with ${n} using ${re}`);
    }
  }
});

test('rejects numbers with leading zeros or wrong width', () => {
  const re = rangeToRegex(1, 100);
  assert.equal(re.test('1'), true);
  assert.equal(re.test('100'), true);
  assert.equal(re.test('0'), false);
  assert.equal(re.test('101'), false);
  assert.equal(re.test('01'), false);
  assert.equal(re.test('0100'), false);
});

test('can return an unanchored pattern', () => {
  const re = rangeToRegex(1, 100, { anchors: false });
  assert.equal(re.test('value 42'), true);
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { parseRange, rangeToRegex } from '../src/range-to-regex.js';

test('parseRange parses "min-max"', () => {
  assert.deepEqual(parseRange('1-100'), { min: 1, max: 100 });
  assert.deepEqual(parseRange(' 10 - 20 '), { min: 10, max: 20 });
});

test('parseRange parses a single value', () => {
  assert.deepEqual(parseRange('42'), { min: 42, max: 42 });
  assert.deepEqual(parseRange(7), { min: 7, max: 7 });
});

test('parseRange rejects malformed input', () => {
  assert.throws(() => parseRange('abc'), SyntaxError);
  assert.throws(() => parseRange('100-1'), RangeError);
  assert.throws(() => parseRange({}), TypeError);
});

test('rangeToRegex matches every number in 1-100 and nothing else', () => {
  const regex = rangeToRegex('1-100');
  for (let n = 1; n <= 100; n += 1) {
    assert.ok(regex.test(String(n)), `${n} should match`);
  }
  for (const n of ['0', '101', '1000', '01', '-1', '1.5']) {
    assert.ok(!regex.test(n), `${n} should not match`);
  }
});

test('rangeToRegex handles a range crossing digit boundaries', () => {
  const regex = rangeToRegex('98-102');
  assert.ok(regex.test('98'));
  assert.ok(regex.test('99'));
  assert.ok(regex.test('100'));
  assert.ok(regex.test('101'));
  assert.ok(regex.test('102'));
  assert.ok(!regex.test('97'));
  assert.ok(!regex.test('103'));
});

test('rangeToRegex anchors the pattern', () => {
  const regex = rangeToRegex('1-10');
  assert.ok(!regex.test('110'));
  assert.ok(!regex.test('x5x'));
  assert.equal(regex.source.startsWith('^'), true);
  assert.equal(regex.source.endsWith('$'), true);
});

test('rangeToRegex supports a capturing group option', () => {
  const regex = rangeToRegex('1-3', { capture: true });
  const match = regex.exec('2');
  assert.equal(match[1], '2');
});

test('rangeToRegex handles a single value and negatives', () => {
  assert.ok(rangeToRegex('42').test('42'));
  assert.ok(!rangeToRegex('42').test('41'));
  assert.ok(rangeToRegex('-5--1').test('-3'));
  assert.ok(!rangeToRegex('-5--1').test('0'));
});

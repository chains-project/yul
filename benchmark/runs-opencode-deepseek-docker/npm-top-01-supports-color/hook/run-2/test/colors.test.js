import test from 'node:test';
import assert from 'node:assert/strict';
import { createColors, detectColorLevel } from '../src/colors.js';

test('createColors disables color at level 0', () => {
  const colors = createColors(0);
  assert.equal(colors.enabled, false);
  assert.equal(colors.red('text'), 'text');
});

test('createColors wraps text with ansi codes when supported', () => {
  const colors = createColors(1);
  assert.equal(colors.enabled, true);
  assert.equal(colors.red('text'), '\u001B[31mtext\u001B[39m');
});

test('createColors coerces non-string values', () => {
  const colors = createColors(1);
  assert.equal(colors.green(42), '\u001B[32m42\u001B[39m');
});

test('detectColorLevel honors FORCE_COLOR', () => {
  const stream = { isTTY: false };
  assert.equal(detectColorLevel({ stream, env: { FORCE_COLOR: '3' } }), 3);
  assert.equal(detectColorLevel({ stream, env: { FORCE_COLOR: '0' } }), 0);
  assert.equal(detectColorLevel({ stream, env: { FORCE_COLOR: 'true' } }), 1);
});

test('detectColorLevel honors NO_COLOR', () => {
  const stream = { isTTY: true, getColorDepth: () => 3 };
  assert.equal(detectColorLevel({ stream, env: { NO_COLOR: '1' } }), 0);
});

test('detectColorLevel disables color for non-tty streams', () => {
  assert.equal(detectColorLevel({ stream: { isTTY: false }, env: {} }), 0);
});

test('detectColorLevel falls back to the stream color depth', () => {
  const stream = { isTTY: true, getColorDepth: () => 2 };
  assert.equal(detectColorLevel({ stream, env: {} }), 2);
});

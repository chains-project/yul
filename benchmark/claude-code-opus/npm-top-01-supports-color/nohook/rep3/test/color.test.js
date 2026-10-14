import { test } from 'node:test';
import assert from 'node:assert/strict';
import { supportsColor, createColors } from '../src/color.js';

const tty = (hasColors = true) => ({ isTTY: true, hasColors: () => hasColors });
const pipe = { isTTY: false };

test('color enabled on a color-capable TTY', () => {
  assert.equal(supportsColor({ stream: tty(), env: {}, argv: [] }), true);
});

test('color disabled on a TTY without color support', () => {
  assert.equal(supportsColor({ stream: tty(false), env: {}, argv: [] }), false);
});

test('color disabled when output is piped', () => {
  assert.equal(supportsColor({ stream: pipe, env: {}, argv: [] }), false);
});

test('NO_COLOR disables color', () => {
  assert.equal(supportsColor({ stream: tty(), env: { NO_COLOR: '1' }, argv: [] }), false);
});

test('empty NO_COLOR is ignored', () => {
  assert.equal(supportsColor({ stream: tty(), env: { NO_COLOR: '' }, argv: [] }), true);
});

test('FORCE_COLOR enables color even when piped', () => {
  assert.equal(supportsColor({ stream: pipe, env: { FORCE_COLOR: '1' }, argv: [] }), true);
});

test('FORCE_COLOR=0 disables color', () => {
  assert.equal(supportsColor({ stream: tty(), env: { FORCE_COLOR: '0' }, argv: [] }), false);
});

test('CLI flags override environment', () => {
  assert.equal(supportsColor({ stream: tty(), env: { FORCE_COLOR: '1' }, argv: ['--no-color'] }), false);
  assert.equal(supportsColor({ stream: pipe, env: { NO_COLOR: '1' }, argv: ['--color'] }), true);
});

test('createColors wraps text only when enabled', () => {
  assert.equal(createColors(true).red('hi'), '\x1b[31mhi\x1b[39m');
  assert.equal(createColors(false).red('hi'), 'hi');
});

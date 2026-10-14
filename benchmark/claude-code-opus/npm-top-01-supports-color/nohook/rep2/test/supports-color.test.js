import { test } from 'node:test';
import assert from 'node:assert/strict';
import { supportsColor } from '../src/supports-color.js';
import { createColors } from '../src/colors.js';

const tty = (hasColors = true) => ({ isTTY: true, hasColors: () => hasColors });
const pipe = { isTTY: false };
const check = (stream, env = {}, argv = []) => supportsColor(stream, { env, argv });

test('enabled on a color-capable TTY', () => {
  assert.equal(check(tty()), true);
});

test('disabled when output is not a TTY', () => {
  assert.equal(check(pipe), false);
});

test('disabled when the terminal reports no color support', () => {
  assert.equal(check(tty(false)), false);
});

test('disabled for TERM=dumb', () => {
  assert.equal(check(tty(), { TERM: 'dumb' }), false);
});

test('NO_COLOR disables colors, but only when non-empty', () => {
  assert.equal(check(tty(), { NO_COLOR: '1' }), false);
  assert.equal(check(tty(), { NO_COLOR: '' }), true);
});

test('NODE_DISABLE_COLORS disables colors', () => {
  assert.equal(check(tty(), { NODE_DISABLE_COLORS: '1' }), false);
});

test('FORCE_COLOR overrides TTY detection', () => {
  assert.equal(check(pipe, { FORCE_COLOR: '1' }), true);
  assert.equal(check(pipe, { FORCE_COLOR: '' }), true);
  assert.equal(check(tty(), { FORCE_COLOR: '0' }), false);
  assert.equal(check(tty(), { FORCE_COLOR: 'false' }), false);
});

test('NO_COLOR beats FORCE_COLOR', () => {
  assert.equal(check(tty(), { NO_COLOR: '1', FORCE_COLOR: '1' }), false);
});

test('CLI flags beat environment variables, last flag wins', () => {
  assert.equal(check(pipe, { NO_COLOR: '1' }, ['--color']), true);
  assert.equal(check(tty(), { FORCE_COLOR: '1' }, ['--no-color']), false);
  assert.equal(check(tty(), {}, ['--color=never']), false);
  assert.equal(check(pipe, {}, ['--color=always']), true);
  assert.equal(check(pipe, {}, ['--no-color', '--color']), true);
});

test('createColors wraps text only when enabled', () => {
  assert.equal(createColors(true).red('x'), '\x1b[31mx\x1b[39m');
  assert.equal(createColors(false).red('x'), 'x');
});

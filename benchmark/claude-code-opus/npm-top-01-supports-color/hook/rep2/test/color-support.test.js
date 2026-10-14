import { test } from 'node:test';
import assert from 'node:assert/strict';
import { getColorLevel } from '../src/color-support.js';
import { createColors } from '../src/colors.js';

const tty = (depth = 8) => ({ isTTY: true, getColorDepth: () => depth });
const pipe = { isTTY: false };
const detect = (stream, env = {}, argv = []) => getColorLevel({ stream, env, argv });

test('non-TTY streams get no color', () => {
  assert.equal(detect(pipe), 0);
});

test('TTY uses Node color depth', () => {
  assert.equal(detect(tty(1)), 0);
  assert.equal(detect(tty(4)), 1);
  assert.equal(detect(tty(8)), 2);
  assert.equal(detect(tty(24)), 3);
});

test('TERM=dumb disables color', () => {
  assert.equal(detect(tty(), { TERM: 'dumb' }), 0);
});

test('NO_COLOR disables color, even on a TTY', () => {
  assert.equal(detect(tty(), { NO_COLOR: '1' }), 0);
});

test('empty NO_COLOR is ignored', () => {
  assert.equal(detect(tty(8), { NO_COLOR: '' }), 2);
});

test('FORCE_COLOR overrides TTY detection', () => {
  assert.equal(detect(pipe, { FORCE_COLOR: '1' }), 1);
  assert.equal(detect(pipe, { FORCE_COLOR: '3' }), 3);
  assert.equal(detect(pipe, { FORCE_COLOR: '' }), 1);
  assert.equal(detect(tty(), { FORCE_COLOR: '0' }), 0);
  assert.equal(detect(tty(), { FORCE_COLOR: 'false' }), 0);
});

test('NO_COLOR beats FORCE_COLOR', () => {
  assert.equal(detect(pipe, { NO_COLOR: '1', FORCE_COLOR: '1' }), 0);
});

test('CLI flags beat environment', () => {
  assert.equal(detect(tty(), {}, ['--no-color']), 0);
  assert.equal(detect(pipe, { NO_COLOR: '1' }, ['--color']), 1);
});

test('disabled palette returns plain text', () => {
  const c = createColors(false);
  assert.equal(c.red('hi'), 'hi');
  assert.equal(createColors(true).red('hi'), '\x1b[31mhi\x1b[39m');
});

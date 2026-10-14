import { test } from 'node:test';
import assert from 'node:assert/strict';
import { colorDepth, createColors } from '../src/color.js';

const tty = { isTTY: true, getColorDepth: () => 8 };
const pipe = { isTTY: false };
const opts = (env = {}, argv = []) => ({ env, argv });

test('TTY uses Node detection', () => assert.equal(colorDepth(tty, opts()), 256));
test('non-TTY disables color', () => assert.equal(colorDepth(pipe, opts()), 0));
test('TERM=dumb disables color', () => assert.equal(colorDepth(tty, opts({ TERM: 'dumb' })), 0));
test('NO_COLOR disables color', () => assert.equal(colorDepth(tty, opts({ NO_COLOR: '1' })), 0));
test('empty NO_COLOR is ignored', () => assert.equal(colorDepth(tty, opts({ NO_COLOR: '' })), 256));
test('FORCE_COLOR enables on pipe', () => assert.equal(colorDepth(pipe, opts({ FORCE_COLOR: '3' })), 16777216));
test('FORCE_COLOR=0 disables', () => assert.equal(colorDepth(tty, opts({ FORCE_COLOR: '0' })), 0));
test('--no-color beats FORCE_COLOR', () =>
  assert.equal(colorDepth(tty, opts({ FORCE_COLOR: '1' }, ['--no-color'])), 0));
test('--color forces on pipe', () => assert.equal(colorDepth(pipe, opts({}, ['--color'])), 16));

test('helpers are plain text when disabled', () => {
  assert.equal(createColors(pipe, opts()).red('hi'), 'hi');
  assert.equal(createColors(tty, opts()).red('hi'), '\x1b[31mhi\x1b[39m');
});

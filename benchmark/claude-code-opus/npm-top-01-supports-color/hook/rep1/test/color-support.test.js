import { test } from 'node:test';
import assert from 'node:assert/strict';
import { detectColorLevel, createColors } from '../src/index.js';

const tty = (depth = 8) => ({ isTTY: true, getColorDepth: () => depth });
const pipe = { isTTY: false };
const opts = (env = {}, argv = []) => ({ env, argv });

test('non-TTY stream has no color', () => {
  assert.equal(detectColorLevel(pipe, opts()), 0);
});

test('TTY uses getColorDepth', () => {
  assert.equal(detectColorLevel(tty(4), opts()), 1);
  assert.equal(detectColorLevel(tty(8), opts()), 2);
  assert.equal(detectColorLevel(tty(24), opts()), 3);
  assert.equal(detectColorLevel(tty(1), opts()), 0);
});

test('TERM=dumb disables color', () => {
  assert.equal(detectColorLevel(tty(), opts({ TERM: 'dumb' })), 0);
});

test('NO_COLOR disables color; empty value is ignored', () => {
  assert.equal(detectColorLevel(tty(), opts({ NO_COLOR: '1' })), 0);
  assert.equal(detectColorLevel(tty(), opts({ NO_COLOR: '' })), 2);
});

test('FORCE_COLOR overrides NO_COLOR and non-TTY', () => {
  assert.equal(detectColorLevel(pipe, opts({ FORCE_COLOR: '1' })), 1);
  assert.equal(detectColorLevel(pipe, opts({ FORCE_COLOR: '' })), 1);
  assert.equal(detectColorLevel(pipe, opts({ FORCE_COLOR: '3' })), 3);
  assert.equal(detectColorLevel(tty(), opts({ FORCE_COLOR: '0' })), 0);
  assert.equal(detectColorLevel(pipe, opts({ FORCE_COLOR: '1', NO_COLOR: '1' })), 1);
});

test('CLI flags take highest precedence', () => {
  assert.equal(detectColorLevel(tty(), opts({ FORCE_COLOR: '3' }, ['--no-color'])), 0);
  assert.equal(detectColorLevel(pipe, opts({ NO_COLOR: '1' }, ['--color'])), 1);
  assert.equal(detectColorLevel(pipe, opts({}, ['--color=256'])), 2);
  assert.equal(detectColorLevel(tty(), opts({}, ['--color=never'])), 0);
});

test('flags after -- are ignored', () => {
  assert.equal(detectColorLevel(tty(), opts({}, ['--', '--no-color'])), 2);
});

test('createColors emits ANSI only when supported', () => {
  assert.equal(createColors(tty(), opts()).red('x'), '\x1b[31mx\x1b[39m');
  assert.equal(createColors(pipe, opts()).red('x'), 'x');
});

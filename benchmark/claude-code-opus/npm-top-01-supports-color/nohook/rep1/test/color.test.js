import { test } from 'node:test';
import assert from 'node:assert/strict';
import { supportsColor, createColors } from '../src/color.js';

const tty = { isTTY: true, hasColors: () => true };
const pipe = { isTTY: false };

test('piped output has no color by default', () => {
  assert.equal(supportsColor(pipe, { argv: [], env: {} }), false);
});

test('TTY with color support enables color', () => {
  assert.equal(supportsColor(tty, { argv: [], env: {} }), true);
});

test('TTY without color support (hasColors false) disables color', () => {
  const mono = { isTTY: true, hasColors: () => false };
  assert.equal(supportsColor(mono, { argv: [], env: {} }), false);
});

test('NO_COLOR disables color on a TTY', () => {
  assert.equal(supportsColor(tty, { argv: [], env: { NO_COLOR: '1' } }), false);
});

test('empty NO_COLOR is ignored', () => {
  assert.equal(supportsColor(tty, { argv: [], env: { NO_COLOR: '' } }), true);
});

test('TERM=dumb disables color', () => {
  assert.equal(supportsColor(tty, { argv: [], env: { TERM: 'dumb' } }), false);
});

test('FORCE_COLOR enables color when piped', () => {
  assert.equal(supportsColor(pipe, { argv: [], env: { FORCE_COLOR: '1' } }), true);
  assert.equal(supportsColor(pipe, { argv: [], env: { FORCE_COLOR: '' } }), true);
});

test('FORCE_COLOR=0 disables color', () => {
  assert.equal(supportsColor(tty, { argv: [], env: { FORCE_COLOR: '0' } }), false);
});

test('CLI flags override environment', () => {
  assert.equal(supportsColor(pipe, { argv: ['--color'], env: { NO_COLOR: '1' } }), true);
  assert.equal(supportsColor(tty, { argv: ['--no-color'], env: { FORCE_COLOR: '1' } }), false);
});

test('createColors returns plain text when disabled', () => {
  const c = createColors(pipe, { argv: [], env: {} });
  assert.equal(c.enabled, false);
  assert.equal(c.red('hi'), 'hi');
});

test('createColors wraps text in ANSI codes when enabled', () => {
  const c = createColors(tty, { argv: [], env: {} });
  assert.equal(c.red('hi'), '\x1b[31mhi\x1b[39m');
  assert.equal(c.bold('hi'), '\x1b[1mhi\x1b[22m');
});

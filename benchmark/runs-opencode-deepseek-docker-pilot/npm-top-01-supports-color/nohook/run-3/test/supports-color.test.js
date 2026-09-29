import test from 'node:test';
import assert from 'node:assert/strict';
import { detectColorLevel } from '../src/supports-color.js';

const tty = { isTTY: true };
const pipe = { isTTY: false };

test('returns 0 when the stream is not a TTY', () => {
  assert.equal(detectColorLevel(pipe, { TERM: 'xterm-256color' }, []), 0);
});

test('NO_COLOR disables color even on a TTY', () => {
  assert.equal(detectColorLevel(tty, { NO_COLOR: '1', TERM: 'xterm-256color' }, []), 0);
});

test('--no-color flag disables color', () => {
  assert.equal(detectColorLevel(tty, { TERM: 'xterm-256color' }, ['--no-color']), 0);
});

test('FORCE_COLOR overrides a non-TTY stream', () => {
  assert.equal(detectColorLevel(pipe, { FORCE_COLOR: '3' }, []), 3);
});

test('--color flag enables color for a non-TTY stream', () => {
  assert.equal(detectColorLevel(pipe, {}, ['--color']), 1);
});

test('TERM=256color yields level 2', () => {
  assert.equal(detectColorLevel(tty, { TERM: 'xterm-256color' }, []), 2);
});

test('COLORTERM=truecolor yields level 3', () => {
  assert.equal(detectColorLevel(tty, { COLORTERM: 'truecolor' }, []), 3);
});

test('TERM=dumb disables color', () => {
  assert.equal(detectColorLevel(tty, { TERM: 'dumb' }, []), 0);
});

test('flat TTY yields level 1', () => {
  assert.equal(detectColorLevel(tty, { TERM: 'xterm' }, []), 1);
});

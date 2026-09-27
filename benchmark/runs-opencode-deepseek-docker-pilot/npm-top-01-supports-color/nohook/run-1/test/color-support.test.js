import assert from 'node:assert/strict';
import { test } from 'node:test';
import { LEVELS, createColors, detectColorSupport, supportsColor } from '../lib/color-support.js';

const tty = { isTTY: true };
const finders = { argv: [], stream: tty, env: {} };

test('reports no color when output is not a TTY', () => {
  const result = detectColorSupport({ ...finders, stream: { isTTY: false } });
  assert.equal(result.level, LEVELS.NONE);
  assert.equal(supportsColor({ ...finders, stream: { isTTY: false } }), false);
});

test('detects basic color on a TTY with TERM set', () => {
  const result = detectColorSupport({ ...finders, env: { TERM: 'xterm' } });
  assert.equal(result.level, LEVELS.BASIC);
});

test('detects 256 color terminals', () => {
  const result = detectColorSupport({ ...finders, env: { TERM: 'xterm-256color' } });
  assert.equal(result.level, LEVELS.ANSI256);
});

test('detects truecolor via COLORTERM', () => {
  const result = detectColorSupport({ ...finders, env: { TERM: 'xterm-256color', COLORTERM: 'truecolor' } });
  assert.equal(result.level, LEVELS.TRUECOLOR);
});

test('NO_COLOR disables color', () => {
  const result = detectColorSupport({ ...finders, env: { TERM: 'xterm-256color', NO_COLOR: '1' } });
  assert.equal(result.level, LEVELS.NONE);
});

test('TERM=dumb disables color', () => {
  const result = detectColorSupport({ ...finders, env: { TERM: 'dumb' } });
  assert.equal(result.level, LEVELS.NONE);
});

test('FORCE_COLOR overrides a non-TTY stream', () => {
  const result = detectColorSupport({ ...finders, stream: { isTTY: false }, env: { FORCE_COLOR: '1' } });
  assert.equal(result.level, LEVELS.BASIC);
});

test('FORCE_COLOR=0 wins over a color-capable terminal', () => {
  const result = detectColorSupport({ ...finders, env: { TERM: 'xterm-256color', FORCE_COLOR: '0' } });
  assert.equal(result.level, LEVELS.NONE);
});

test('--no-color flag disables color', () => {
  const result = detectColorSupport({ ...finders, env: { TERM: 'xterm-256color' }, argv: ['--no-color'] });
  assert.equal(result.level, LEVELS.NONE);
});

test('known CI environment enables basic color without a TTY', () => {
  const result = detectColorSupport({
    ...finders,
    stream: { isTTY: false },
    env: { CI: 'true', GITHUB_ACTIONS: 'true' },
  });
  assert.equal(result.level, LEVELS.BASIC);
});

test('createColors emits ANSI when supported and plain text when not', () => {
  const colored = createColors(LEVELS.BASIC);
  assert.equal(colored.green('ok'), '\u001B[32mok\u001B[0m');

  const plain = createColors(LEVELS.NONE);
  assert.equal(plain.green('ok'), 'ok');
  assert.equal(plain.rgb(1, 2, 3)('ok'), 'ok');
});

test('rgb only emits codes at truecolor level', () => {
  assert.equal(createColors(LEVELS.ANSI256).rgb(1, 2, 3)('x'), 'x');
  assert.equal(createColors(LEVELS.TRUECOLOR).rgb(1, 2, 3)('x'), '\u001B[38;2;1;2;3mx\u001B[0m');
});

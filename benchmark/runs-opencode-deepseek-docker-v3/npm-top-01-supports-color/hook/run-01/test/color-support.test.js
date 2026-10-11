import { test } from 'node:test';
import assert from 'node:assert/strict';
import process from 'node:process';
import { detectColorSupport, createStyler } from '../src/color-support.js';

const COLOR_ENV_KEYS = [
  'FORCE_COLOR',
  'NO_COLOR',
  'TERM',
  'COLORTERM',
  'WT_SESSION',
  'TERM_PROGRAM',
  'CI',
  'GITHUB_ACTIONS',
];

function withEnv(values, fn) {
  const saved = new Map();
  for (const key of COLOR_ENV_KEYS) {
    saved.set(key, process.env[key]);
    delete process.env[key];
  }
  Object.assign(process.env, values);
  try {
    return fn();
  } finally {
    for (const key of COLOR_ENV_KEYS) {
      const original = saved.get(key);
      if (original === undefined) delete process.env[key];
      else process.env[key] = original;
    }
  }
}

const TTY = { isTTY: true };
const PIPE = { isTTY: false };

test('returns 0 for a non-TTY stream', () => {
  withEnv({}, () => {
    assert.equal(detectColorSupport(PIPE, []), 0);
  });
});

test('returns basic color for a TTY', () => {
  withEnv({ TERM: 'xterm-256color' }, () => {
    assert.equal(detectColorSupport(TTY, []), 2);
  });
});

test('--no-color disables color even on a TTY', () => {
  withEnv({ TERM: 'xterm-256color' }, () => {
    assert.equal(detectColorSupport(TTY, ['node', 'cli', '--no-color']), 0);
  });
});

test('--color forces color through a pipe', () => {
  withEnv({}, () => {
    assert.equal(detectColorSupport(PIPE, ['node', 'cli', '--color']), 1);
  });
});

test('NO_COLOR disables color', () => {
  withEnv({ NO_COLOR: '1', TERM: 'xterm-256color' }, () => {
    assert.equal(detectColorSupport(TTY, []), 0);
  });
});

test('FORCE_COLOR wins over NO_COLOR', () => {
  withEnv({ FORCE_COLOR: '1', NO_COLOR: '1' }, () => {
    assert.equal(detectColorSupport(PIPE, []), 1);
  });
});

test('FORCE_COLOR=3 enables truecolor', () => {
  withEnv({ FORCE_COLOR: '3' }, () => {
    assert.equal(detectColorSupport(PIPE, []), 3);
  });
});

test('TERM=dumb disables color', () => {
  withEnv({ TERM: 'dumb' }, () => {
    assert.equal(detectColorSupport(TTY, []), 0);
  });
});

test('COLORTERM=truecolor enables truecolor', () => {
  withEnv({ TERM: 'xterm', COLORTERM: 'truecolor' }, () => {
    assert.equal(detectColorSupport(TTY, []), 3);
  });
});

test('CI provider enables color without a TTY', () => {
  withEnv({ CI: 'true', GITHUB_ACTIONS: 'true' }, () => {
    assert.equal(detectColorSupport(PIPE, []), 1);
  });
});

test('styler wraps text when color is supported', () => {
  const style = createStyler(1);
  assert.equal(style('hi', 'green'), '\u001B[32mhi\u001B[0m');
});

test('styler returns plain text at level 0', () => {
  const style = createStyler(0);
  assert.equal(style('hi', 'green', 'bold'), 'hi');
});

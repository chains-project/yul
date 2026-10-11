import test from 'node:test';
import assert from 'node:assert/strict';
import { detectColorLevel, supportsColor, LEVEL } from '../src/color-support.js';

const TTY = { isTTY: true };
const PIPE = { isTTY: false };

function withEnv(vars, fn) {
  const saved = {};
  for (const [key, value] of Object.entries(vars)) {
    saved[key] = process.env[key];
    if (value === undefined) delete process.env[key];
    else process.env[key] = value;
  }
  try {
    return fn();
  } finally {
    for (const [key, value] of Object.entries(saved)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
  }
}

test('returns NONE for a non-tty stream', () => {
  withEnv({ TERM: 'xterm-256color', NO_COLOR: undefined, FORCE_COLOR: undefined, CI: undefined }, () => {
    assert.equal(detectColorLevel(PIPE), LEVEL.NONE);
    assert.equal(supportsColor(PIPE), false);
  });
});

test('returns NONE when NO_COLOR is set', () => {
  withEnv({ NO_COLOR: '1', TERM: 'xterm-256color', FORCE_COLOR: undefined }, () => {
    assert.equal(detectColorLevel(TTY), LEVEL.NONE);
  });
});

test('FORCE_COLOR overrides tty detection', () => {
  withEnv({ FORCE_COLOR: '1', NO_COLOR: undefined }, () => {
    assert.equal(detectColorLevel(PIPE), LEVEL.BASIC);
  });
});

test('detects truecolor through COLORTERM', () => {
  withEnv(
    { COLORTERM: 'truecolor', TERM: 'xterm-256color', NO_COLOR: undefined, FORCE_COLOR: undefined, CI: undefined },
    () => assert.equal(detectColorLevel(TTY), LEVEL.TRUECOLOR),
  );
});

test('detects ansi256 through TERM', () => {
  withEnv(
    { COLORTERM: undefined, TERM: 'xterm-256color', NO_COLOR: undefined, FORCE_COLOR: undefined, CI: undefined },
    () => assert.equal(detectColorLevel(TTY), LEVEL.ANSI256),
  );
});

test('returns NONE for TERM=dumb', () => {
  withEnv(
    { COLORTERM: undefined, TERM: 'dumb', NO_COLOR: undefined, FORCE_COLOR: undefined, CI: undefined },
    () => assert.equal(detectColorLevel(TTY), LEVEL.NONE),
  );
});

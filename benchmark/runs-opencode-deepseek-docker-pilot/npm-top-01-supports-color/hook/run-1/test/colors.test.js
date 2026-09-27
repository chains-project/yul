import { test } from 'node:test';
import assert from 'node:assert/strict';
import { colorLevel, supportsColor, createColors } from '../src/colors.js';

const tty = (depth) => ({
  isTTY: true,
  getColorDepth: () => depth,
});

const nonTty = { isTTY: false };

function withEnv(vars, fn) {
  const saved = {};
  for (const key of Object.keys(vars)) saved[key] = process.env[key];
  for (const [key, value] of Object.entries(vars)) {
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

test('empty env with no TTY disables color', () => {
  withEnv({ NO_COLOR: undefined, FORCE_COLOR: undefined }, () => {
    assert.equal(colorLevel(nonTty), 0);
    assert.equal(supportsColor(nonTty), false);
  });
});

test('a TTY with hasColors() enables basic color', () => {
  withEnv({ NO_COLOR: undefined, FORCE_COLOR: undefined, TERM: 'xterm-256color' }, () => {
    assert.equal(colorLevel({ isTTY: true, hasColors: () => true }), 1);
  });
});

test('a TTY without any detection API is treated as no color', () => {
  withEnv({ NO_COLOR: undefined, FORCE_COLOR: undefined, TERM: 'xterm-256color' }, () => {
    assert.equal(colorLevel({ isTTY: true }), 0);
  });
});

test('maps terminal color depth to a level', () => {
  withEnv({ NO_COLOR: undefined, FORCE_COLOR: undefined }, () => {
    assert.equal(colorLevel(tty(1)), 0);
    assert.equal(colorLevel(tty(4)), 1);
    assert.equal(colorLevel(tty(8)), 2);
    assert.equal(colorLevel(tty(24)), 3);
  });
});

test('NO_COLOR wins over a color-capable TTY', () => {
  withEnv({ NO_COLOR: '1', FORCE_COLOR: undefined }, () => {
    assert.equal(colorLevel(tty(24)), 0);
  });
});

test('FORCE_COLOR enables color on a non-TTY', () => {
  withEnv({ NO_COLOR: undefined, FORCE_COLOR: '1' }, () => {
    assert.equal(colorLevel(nonTty), 1);
  });
});

test('FORCE_COLOR=0 disables color on a TTY', () => {
  withEnv({ NO_COLOR: undefined, FORCE_COLOR: '0' }, () => {
    assert.equal(colorLevel(tty(24)), 0);
  });
});

test('TERM=dumb disables color', () => {
  withEnv({ NO_COLOR: undefined, FORCE_COLOR: undefined, TERM: 'dumb' }, () => {
    assert.equal(colorLevel(tty(24)), 0);
  });
});

test('helpers wrap text when enabled and pass through when disabled', () => {
  withEnv({ NO_COLOR: undefined, FORCE_COLOR: '1' }, () => {
    assert.equal(createColors(nonTty).green('hi'), '\x1b[32mhi\x1b[0m');
  });
  withEnv({ NO_COLOR: undefined, FORCE_COLOR: '0' }, () => {
    assert.equal(createColors(tty(24)).green('hi'), 'hi');
  });
});

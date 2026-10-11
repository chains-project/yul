import test from "node:test";
import assert from "node:assert/strict";
import {
  getColorSupport,
  supportsColor,
  translateLevel,
  forceColorLevel,
  sniffColorFlags,
} from "../src/color-support.js";

const MANAGED = [
  "FORCE_COLOR",
  "NO_COLOR",
  "NODE_DISABLE_COLORS",
  "TERM",
  "COLORTERM",
  "TERM_PROGRAM",
  "CI",
  "CONTINUOUS_INTEGRATION",
  "BUILD_NUMBER",
  "GITHUB_ACTIONS",
  "WT_SESSION",
  "ANSICON",
  "ConEmuANSI",
];

function withEnv(overrides, fn) {
  const saved = {};
  for (const key of MANAGED) {
    saved[key] = Object.prototype.hasOwnProperty.call(process.env, key)
      ? process.env[key]
      : undefined;
    delete process.env[key];
  }
  Object.assign(process.env, overrides);

  try {
    return fn();
  } finally {
    for (const key of MANAGED) {
      if (saved[key] === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = saved[key];
      }
    }
  }
}

const tty = { isTTY: true };
const notTty = { isTTY: false };

test("translateLevel clamps and derives flags", () => {
  assert.deepEqual(translateLevel(0), {
    level: 0,
    supported: false,
    hasBasic: false,
    has256: false,
    has16m: false,
  });
  const truecolor = translateLevel(9);
  assert.equal(truecolor.level, 3);
  assert.equal(truecolor.has16m, true);
  assert.equal(truecolor.has256, true);
});

test("FORCE_COLOR overrides everything", () => {
  withEnv({ FORCE_COLOR: "3" }, () => {
    assert.equal(getColorSupport(notTty).level, 3);
  });
  withEnv({ FORCE_COLOR: "0", TERM: "xterm-256color" }, () => {
    assert.equal(getColorSupport(tty).level, 0);
  });
});

test("NO_COLOR disables color when not forced", () => {
  withEnv({ NO_COLOR: "1", TERM: "xterm-256color" }, () => {
    assert.equal(getColorSupport(tty).supported, false);
  });
});

test("dumb terminals report no color", () => {
  withEnv({ TERM: "dumb" }, () => {
    assert.equal(getColorSupport(tty).supported, false);
  });
});

test("non-TTY without CI reports no color", () => {
  withEnv({ TERM: "xterm-256color" }, () => {
    assert.equal(getColorSupport(notTty).supported, false);
  });
});

test("TTY TERM values map to correct levels", () => {
  withEnv({ TERM: "xterm" }, () => {
    assert.equal(getColorSupport(tty).level, 1);
  });
  withEnv({ TERM: "xterm-256color" }, () => {
    assert.equal(getColorSupport(tty).level, 2);
  });
  withEnv({ TERM: "xterm", COLORTERM: "truecolor" }, () => {
    assert.equal(getColorSupport(tty).level, 3);
  });
});

test("supportsColor returns a boolean", () => {
  withEnv({ TERM: "xterm" }, () => {
    assert.equal(supportsColor(tty), true);
  });
});

test("sniffColorFlags parses common flags", () => {
  assert.equal(sniffColorFlags(["--no-color"]), 0);
  assert.equal(sniffColorFlags(["--color"]), 1);
  assert.equal(sniffColorFlags(["--color=256"]), 2);
  assert.equal(sniffColorFlags(["--color=16m"]), 3);
  assert.equal(sniffColorFlags([]), undefined);
});

test("forceColorLevel reads FORCE_COLOR", () => {
  withEnv({}, () => {
    assert.equal(forceColorLevel(), undefined);
  });
  withEnv({ FORCE_COLOR: "true" }, () => {
    assert.equal(forceColorLevel(), 1);
  });
});

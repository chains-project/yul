import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { resolveRealPath } from "../src/realpath.js";

test("resolves a symlink to its canonical target", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "resolve-realpath-"));
  const real = path.join(dir, "real");
  const link = path.join(dir, "link");
  fs.mkdirSync(real);
  fs.writeFileSync(path.join(real, "file.txt"), "hi");
  fs.symlinkSync(real, link);

  assert.equal(resolveRealPath(path.join(link, "file.txt")), path.join(real, "file.txt"));
});

test("rejects a non-string path", () => {
  assert.throws(() => resolveRealPath(null), TypeError);
});

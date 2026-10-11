import { test } from "node:test";
import assert from "node:assert/strict";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";

import { resolve } from "../src/index.js";

interface Fixture {
  root: string;
  write(rel: string, contents?: string): string;
  cleanup(): void;
}

function fixture(): Fixture {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "resolver-"));
  return {
    root,
    write(rel, contents = "") {
      const abs = path.join(root, rel);
      fs.mkdirSync(path.dirname(abs), { recursive: true });
      fs.writeFileSync(abs, contents);
      return abs;
    },
    cleanup() {
      fs.rmSync(root, { recursive: true, force: true });
    },
  };
}

test("returns built-in modules as-is", () => {
  assert.equal(resolve("fs"), "fs");
  assert.equal(resolve("node:path"), "node:path");
});

test("resolves a relative file with an explicit extension", () => {
  const f = fixture();
  try {
    const file = f.write("src/a.js", "");
    assert.equal(resolve("./a.js", { basedir: path.join(f.root, "src") }), fs.realpathSync(file));
  } finally {
    f.cleanup();
  }
});

test("adds missing extensions in order", () => {
  const f = fixture();
  try {
    const file = f.write("src/a.json", "{}");
    assert.equal(resolve("./a", { basedir: path.join(f.root, "src") }), fs.realpathSync(file));
  } finally {
    f.cleanup();
  }
});

test("resolves a directory index", () => {
  const f = fixture();
  try {
    const file = f.write("src/dir/index.js", "");
    assert.equal(resolve("./dir", { basedir: path.join(f.root, "src") }), fs.realpathSync(file));
  } finally {
    f.cleanup();
  }
});

test("honours package.json main", () => {
  const f = fixture();
  try {
    f.write("pkg/package.json", JSON.stringify({ main: "./lib/entry.js" }));
    const file = f.write("pkg/lib/entry.js", "");
    assert.equal(resolve("./pkg", { basedir: f.root }), fs.realpathSync(file));
  } finally {
    f.cleanup();
  }
});

test("walks up node_modules directories", () => {
  const f = fixture();
  try {
    const file = f.write("node_modules/foo/index.js", "");
    const basedir = path.join(f.root, "a", "b", "c");
    fs.mkdirSync(basedir, { recursive: true });
    assert.equal(resolve("foo", { basedir }), fs.realpathSync(file));
  } finally {
    f.cleanup();
  }
});

test("resolves scoped packages and subpaths", () => {
  const f = fixture();
  try {
    const file = f.write("node_modules/@scope/foo/bar.js", "");
    assert.equal(resolve("@scope/foo/bar.js", { basedir: f.root }), fs.realpathSync(file));
  } finally {
    f.cleanup();
  }
});

test("supports exports subpath maps, patterns and conditions", () => {
  const f = fixture();
  try {
    f.write(
      "node_modules/foo/package.json",
      JSON.stringify({
        name: "foo",
        exports: {
          ".": { node: "./dist/index.node.js", default: "./dist/index.js" },
          "./feature": "./dist/feature.js",
          "./lib/*": "./src/*.js",
        },
      }),
    );
    const index = f.write("node_modules/foo/dist/index.node.js", "");
    const feature = f.write("node_modules/foo/dist/feature.js", "");
    const pattern = f.write("node_modules/foo/src/util.js", "");

    assert.equal(resolve("foo", { basedir: f.root }), fs.realpathSync(index));
    assert.equal(resolve("foo/feature", { basedir: f.root }), fs.realpathSync(feature));
    assert.equal(resolve("foo/lib/util", { basedir: f.root }), fs.realpathSync(pattern));
  } finally {
    f.cleanup();
  }
});

test("prefers require condition for CJS resolution", () => {
  const f = fixture();
  try {
    f.write(
      "node_modules/foo/package.json",
      JSON.stringify({
        name: "foo",
        exports: { ".": { import: "./esm.js", require: "./cjs.js" } },
      }),
    );
    const cjs = f.write("node_modules/foo/cjs.js", "");
    assert.equal(resolve("foo", { basedir: f.root }), fs.realpathSync(cjs));
  } finally {
    f.cleanup();
  }
});

test("throws MODULE_NOT_FOUND for missing modules", () => {
  const f = fixture();
  try {
    assert.throws(
      () => resolve("does-not-exist", { basedir: f.root }),
      (err: NodeJS.ErrnoException) => err.code === "MODULE_NOT_FOUND",
    );
  } finally {
    f.cleanup();
  }
});

import { test } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { createResolver, resolve } from "../src/index.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const project = path.join(here, "fixtures", "project");
const entry = path.join(project, "src", "index.js");
const srcDir = path.join(project, "src");
const depMain = path.join(project, "node_modules", "dep", "lib", "main.js");

test("resolves builtin specifiers", () => {
  assert.equal(resolve("node:path"), "node:path");
  assert.equal(resolve("fs"), "fs");
});

test("resolves relative specifiers from a file", () => {
  assert.equal(resolve("./feature.js", { from: entry }), path.join(srcDir, "feature.js"));
});

test("resolves relative specifiers from a directory", () => {
  assert.equal(resolve("./feature.js", { from: srcDir }), path.join(srcDir, "feature.js"));
});

test("resolves package specifiers through node_modules", () => {
  assert.equal(resolve("dep", { from: entry }), depMain);
});

test("matches node's own require.resolve", () => {
  const require = createRequire(entry);
  for (const specifier of ["./feature.js", "dep"]) {
    assert.equal(resolve(specifier, { from: entry }), require.resolve(specifier));
  }
});

test("supports custom lookup paths", () => {
  const require = createRequire(entry);
  const expected = require.resolve("dep", { paths: [project] });
  assert.equal(resolve("dep", { from: entry, paths: [project] }), expected);
});

test("throws on unresolved specifiers", () => {
  assert.throws(() => resolve("./missing.js", { from: entry }), /Cannot find module/);
});

test("createResolver applies defaults and allows overrides", () => {
  const resolveFromEntry = createResolver({ from: entry });
  assert.equal(resolveFromEntry("./feature.js"), path.join(srcDir, "feature.js"));
  assert.equal(
    resolveFromEntry("dep", { from: project }),
    depMain,
  );
});

test("rejects invalid specifiers", () => {
  assert.throws(() => resolve("", { from: entry }), TypeError);
  assert.throws(() => resolve(undefined, { from: entry }), TypeError);
});

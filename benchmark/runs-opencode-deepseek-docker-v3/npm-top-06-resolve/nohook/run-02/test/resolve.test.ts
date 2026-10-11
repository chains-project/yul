import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, before, describe, it } from "node:test";
import {
  nodeModulesPaths,
  resolveFromFile,
  resolveSync,
  ResolveError,
} from "../src/index.ts";

let root: string;

function write(relative: string, contents: string | object): void {
  const file = join(root, relative);
  mkdirSync(join(file, ".."), { recursive: true });
  const data = typeof contents === "string" ? contents : JSON.stringify(contents);
  writeFileSync(file, data);
}

const real = (path: string): string => realpathSync(path);

before(() => {
  root = mkdtempSync(join(tmpdir(), "module-resolver-"));

  write("src/app.js", "module.exports = {};\n");

  write("node_modules/plain/package.json", { main: "lib/entry.js" });
  write("node_modules/plain/lib/entry.js", "");

  write("node_modules/@scope/pkg/package.json", { main: "index.js" });
  write("node_modules/@scope/pkg/index.js", "");

  write("node_modules/exp/package.json", {
    name: "exp",
    exports: {
      ".": { node: { require: "./cjs/index.js" }, default: "./esm/index.js" },
      "./feature": "./feature.js",
      "./plugins/*": "./plugins/*.js",
    },
    imports: { "#internal": "./internal.js" },
  });
  write("node_modules/exp/cjs/index.js", "");
  write("node_modules/exp/esm/index.js", "");
  write("node_modules/exp/feature.js", "");
  write("node_modules/exp/plugins/a.js", "");
  write("node_modules/exp/internal.js", "");

  write("selfpkg/package.json", {
    name: "selfpkg",
    exports: { ".": "./main.js", "./util": "./util.js" },
    imports: { "#util": "./util.js" },
  });
  write("selfpkg/main.js", "");
  write("selfpkg/util.js", "");
  write("selfpkg/nested/consumer.js", "");
});

after(() => {
  rmSync(root, { recursive: true, force: true });
});

describe("core and relative resolution", () => {
  it("returns core module specifiers untouched", () => {
    assert.equal(resolveSync("fs", { basedir: root }), "fs");
    assert.equal(resolveSync("node:path", { basedir: root }), "node:path");
  });

  it("resolves relative files and appends extensions", () => {
    assert.equal(
      resolveSync("./app", { basedir: join(root, "src") }),
      real(join(root, "src/app.js")),
    );
  });

  it("throws MODULE_NOT_FOUND for missing relative files", () => {
    assert.throws(
      () => resolveSync("./missing", { basedir: join(root, "src") }),
      (error: unknown) =>
        error instanceof ResolveError && error.code === "MODULE_NOT_FOUND",
    );
  });
});

describe("node_modules resolution", () => {
  it("resolves a package via package.json main", () => {
    assert.equal(
      resolveSync("plain", { basedir: join(root, "src") }),
      real(join(root, "node_modules/plain/lib/entry.js")),
    );
  });

  it("resolves scoped packages", () => {
    assert.equal(
      resolveSync("@scope/pkg", { basedir: join(root, "src") }),
      real(join(root, "node_modules/@scope/pkg/index.js")),
    );
  });

  it("resolves subpaths inside a package", () => {
    assert.equal(
      resolveSync("@scope/pkg/index.js", { basedir: join(root, "src") }),
      real(join(root, "node_modules/@scope/pkg/index.js")),
    );
  });

  it("builds the node_modules search path up to the root", () => {
    const dirs = nodeModulesPaths(join(root, "src"));
    assert.equal(dirs[0], join(root, "src/node_modules"));
    assert.ok(dirs.includes(join(root, "node_modules")));
  });
});

describe("package exports and imports", () => {
  it("honours conditional exports", () => {
    assert.equal(
      resolveSync("exp", { basedir: join(root, "src") }),
      real(join(root, "node_modules/exp/cjs/index.js")),
    );
  });

  it("honours custom conditions", () => {
    assert.equal(
      resolveSync("exp", { basedir: join(root, "src"), conditions: ["default"] }),
      real(join(root, "node_modules/exp/esm/index.js")),
    );
  });

  it("resolves explicit subpath exports", () => {
    assert.equal(
      resolveSync("exp/feature", { basedir: join(root, "src") }),
      real(join(root, "node_modules/exp/feature.js")),
    );
  });

  it("resolves wildcard subpath exports", () => {
    assert.equal(
      resolveSync("exp/plugins/a", { basedir: join(root, "src") }),
      real(join(root, "node_modules/exp/plugins/a.js")),
    );
  });

  it("throws ERR_PACKAGE_PATH_NOT_EXPORTED for unlisted subpaths", () => {
    assert.throws(
      () => resolveSync("exp/private", { basedir: join(root, "src") }),
      (error: unknown) =>
        error instanceof ResolveError &&
        error.code === "ERR_PACKAGE_PATH_NOT_EXPORTED",
    );
  });
});

describe("self-reference and #imports", () => {
  it("resolves a package by its own name", () => {
    assert.equal(
      resolveSync("selfpkg/util", { basedir: join(root, "selfpkg/nested") }),
      real(join(root, "selfpkg/util.js")),
    );
  });

  it("resolves #imports from the nearest package.json", () => {
    assert.equal(
      resolveSync("#util", { basedir: join(root, "selfpkg/nested") }),
      real(join(root, "selfpkg/util.js")),
    );
  });
});

describe("resolveFromFile", () => {
  it("resolves relative to the importing file's directory", () => {
    assert.equal(
      resolveFromFile(join(root, "src/app.js"), "./app"),
      real(join(root, "src/app.js")),
    );
  });
});

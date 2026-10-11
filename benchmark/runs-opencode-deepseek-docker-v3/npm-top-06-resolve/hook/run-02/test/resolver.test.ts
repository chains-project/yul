import { mkdirSync, mkdtempSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { ResolveError, isCoreModule, resolve, resolveModule } from "../src/index.js";

let root: string;
let appDir: string;
let importsDir: string;

function write(relativePath: string, contents = ""): string {
  const full = path.join(root, relativePath);
  mkdirSync(path.dirname(full), { recursive: true });
  writeFileSync(full, contents);
  return full;
}

function at(relativePath: string): string {
  return path.join(appDir, relativePath);
}

beforeEach(() => {
  root = mkdtempSync(path.join(tmpdir(), "node-resolver-"));
  appDir = path.join(root, "app");

  write(
    "app/package.json",
    JSON.stringify({
      name: "app",
      version: "1.0.0",
      exports: {
        ".": "./src/main.js",
        "./util": "./src/util.js",
        "./features/*": "./src/features/*.js",
      },
    })
  );
  write("app/src/main.js");
  write("app/src/util.js");
  write("app/src/features/a.js");
  write("app/nested/index.json", JSON.stringify({ ok: true }));
  write("app/legacy/package.json", JSON.stringify({ name: "legacy", main: "start" }));
  write("app/legacy/start.js");

  write(
    "app/node_modules/foo/package.json",
    JSON.stringify({ name: "foo", version: "1.0.0", main: "lib/main.js" })
  );
  write("app/node_modules/foo/lib/main.js");
  write("app/node_modules/foo/index.js");

  write(
    "app/node_modules/bar/package.json",
    JSON.stringify({
      name: "bar",
      version: "1.0.0",
      exports: {
        ".": "./index.js",
        "./sub": "./sub.js",
        "./glob/*": "./src/*.js",
        "./conditional": { node: "./node.js", default: "./browser.js" },
      },
    })
  );
  write("app/node_modules/bar/index.js");
  write("app/node_modules/bar/sub.js");
  write("app/node_modules/bar/src/a.js");
  write("app/node_modules/bar/node.js");
  write("app/node_modules/bar/browser.js");
  write("app/node_modules/bar/private.js");

  write(
    "app/node_modules/@scope/baz/package.json",
    JSON.stringify({ name: "@scope/baz", version: "1.0.0", exports: "./entry.js" })
  );
  write("app/node_modules/@scope/baz/entry.js");

  importsDir = path.join(appDir, "imports");
  write(
    "app/imports/package.json",
    JSON.stringify({
      name: "imports-app",
      imports: { "#internal": "./lib/internal.js", "#deps/*": "./lib/deps/*.js" },
    })
  );
  write("app/imports/lib/internal.js");
  write("app/imports/lib/deps/x.js");
});

afterEach(() => {
  rmSync(root, { recursive: true, force: true });
});

const raw = { preserveSymlinks: true } as const;

describe("core modules", () => {
  it("detects built-ins", () => {
    expect(isCoreModule("fs")).toBe(true);
    expect(isCoreModule("node:path")).toBe(true);
    expect(isCoreModule("./fs")).toBe(false);
  });

  it("returns the built-in name", () => {
    expect(resolve("fs")).toBe("fs");
    expect(resolve("node:path")).toBe("node:path");
  });

  it("can reject built-ins", () => {
    expect(() => resolve("fs", { includeCoreModules: false })).toThrow(ResolveError);
  });
});

describe("relative and absolute paths", () => {
  it("resolves an exact file", () => {
    expect(resolve("./src/main.js", { basedir: appDir, ...raw })).toBe(at("src/main.js"));
  });

  it("appends extensions in order", () => {
    expect(resolve("./src/util", { basedir: appDir, ...raw })).toBe(at("src/util.js"));
  });

  it("loads a directory index", () => {
    expect(resolve("./nested", { basedir: appDir, ...raw })).toBe(at("nested/index.json"));
  });

  it("honours the package.json main field", () => {
    expect(resolve("./legacy", { basedir: appDir, ...raw })).toBe(at("legacy/start.js"));
  });

  it("resolves an absolute path", () => {
    expect(resolve(at("src/util.js"), { basedir: appDir, ...raw })).toBe(at("src/util.js"));
  });

  it("supports custom extensions", () => {
    write("app/comp/thing.mjs");
    expect(
      resolve("./comp/thing", { basedir: appDir, extensions: [".mjs"], ...raw })
    ).toBe(at("comp/thing.mjs"));
  });
});

describe("node_modules packages", () => {
  it("resolves the package main (legacy)", () => {
    expect(resolve("foo", { basedir: appDir, ...raw })).toBe(
      at("node_modules/foo/lib/main.js")
    );
  });

  it("resolves from a nested directory", () => {
    expect(resolve("foo", { basedir: at("src"), ...raw })).toBe(
      at("node_modules/foo/lib/main.js")
    );
  });

  it("resolves a subpath within a package without exports", () => {
    write("app/node_modules/foo/lib/extra.js");
    expect(resolve("foo/lib/extra", { basedir: appDir, ...raw })).toBe(
      at("node_modules/foo/lib/extra.js")
    );
  });
});

describe("exports map", () => {
  it("resolves the root export", () => {
    expect(resolve("bar", { basedir: appDir, ...raw })).toBe(
      at("node_modules/bar/index.js")
    );
  });

  it("resolves an explicit subpath", () => {
    expect(resolve("bar/sub", { basedir: appDir, ...raw })).toBe(
      at("node_modules/bar/sub.js")
    );
  });

  it("resolves a wildcard subpath", () => {
    expect(resolve("bar/glob/a", { basedir: appDir, ...raw })).toBe(
      at("node_modules/bar/src/a.js")
    );
  });

  it("applies conditions", () => {
    expect(resolve("bar/conditional", { basedir: appDir, ...raw })).toBe(
      at("node_modules/bar/node.js")
    );
    expect(
      resolve("bar/conditional", {
        basedir: appDir,
        conditions: ["browser", "require"],
        ...raw,
      })
    ).toBe(at("node_modules/bar/browser.js"));
  });

  it("supports a top level string export", () => {
    expect(resolve("@scope/baz", { basedir: appDir, ...raw })).toBe(
      at("node_modules/@scope/baz/entry.js")
    );
  });

  it("blocks unexported files", () => {
    expect(() => resolve("bar/private.js", { basedir: appDir, ...raw })).toThrow(
      ResolveError
    );
  });
});

describe("package self-reference", () => {
  it("resolves its own exports", () => {
    expect(resolve("app/util", { basedir: appDir, ...raw })).toBe(at("src/util.js"));
    expect(resolve("app/features/a", { basedir: appDir, ...raw })).toBe(
      at("src/features/a.js")
    );
  });
});

describe("imports map (#)", () => {
  it("resolves an internal import", () => {
    expect(resolve("#internal", { basedir: importsDir, ...raw })).toBe(
      path.join(importsDir, "lib/internal.js")
    );
  });

  it("resolves a wildcard internal import", () => {
    expect(resolve("#deps/x", { basedir: importsDir, ...raw })).toBe(
      path.join(importsDir, "lib/deps/x.js")
    );
  });
});

describe("failures", () => {
  it("throws MODULE_NOT_FOUND for a missing package", () => {
    try {
      resolve("does-not-exist", { basedir: appDir });
      expect.unreachable("should have thrown");
    } catch (error) {
      expect(error).toBeInstanceOf(ResolveError);
      expect((error as ResolveError).code).toBe("MODULE_NOT_FOUND");
    }
  });

  it("rejects an empty specifier", () => {
    expect(() => resolve("")).toThrow(ResolveError);
  });
});

describe("misc", () => {
  it("exposes resolveModule as an alias", () => {
    expect(resolveModule).toBe(resolve);
  });

  it("dereferences symlinks by default", () => {
    // tmpdir may itself be a symlink (e.g. macOS); the default should match realpath.
    const result = resolve("./src/util.js", { basedir: appDir });
    expect(result).toBe(realpathSync(at("src/util.js")));
  });
});

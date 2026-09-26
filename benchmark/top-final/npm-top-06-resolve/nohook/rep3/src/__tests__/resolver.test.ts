import { describe, expect, it } from "vitest";
import path from "node:path";
import {
  isCoreModule,
  ModuleNotFoundError,
  resolveModule,
  resolveModuleAsync,
} from "../resolver";

const fixtures = path.join(__dirname, "fixtures");

describe("isCoreModule", () => {
  it("recognizes Node builtins", () => {
    expect(isCoreModule("fs")).toBe(true);
    expect(isCoreModule("node:path")).toBe(true);
  });

  it("rejects non-builtins", () => {
    expect(isCoreModule("some-dep")).toBe(false);
  });
});

describe("resolveModule", () => {
  it("resolves a relative file, adding an extension", () => {
    const resolved = resolveModule("./fixtures/pkg-with-index/index", {
      basedir: __dirname,
    });
    expect(resolved).toBe(path.join(fixtures, "pkg-with-index", "index.js"));
  });

  it("resolves a directory via its package.json main field", () => {
    const resolved = resolveModule("./fixtures/pkg-with-main", {
      basedir: __dirname,
    });
    expect(resolved).toBe(path.join(fixtures, "pkg-with-main", "lib", "entry.js"));
  });

  it("resolves a directory via index.js when there is no package.json", () => {
    const resolved = resolveModule("./fixtures/pkg-with-index", {
      basedir: __dirname,
    });
    expect(resolved).toBe(path.join(fixtures, "pkg-with-index", "index.js"));
  });

  it("walks up node_modules directories from a nested basedir", () => {
    const resolved = resolveModule("some-dep", {
      basedir: path.join(fixtures, "consumer", "nested", "deep"),
    });
    expect(resolved).toBe(
      path.join(fixtures, "consumer", "node_modules", "some-dep", "index.js"),
    );
  });

  it("throws ModuleNotFoundError for a missing specifier", () => {
    expect(() => resolveModule("does-not-exist", { basedir: fixtures })).toThrow(
      ModuleNotFoundError,
    );
  });
});

describe("resolveModuleAsync", () => {
  it("resolves the same way as the sync API", async () => {
    const resolved = await resolveModuleAsync("./fixtures/pkg-with-main", {
      basedir: __dirname,
    });
    expect(resolved).toBe(path.join(fixtures, "pkg-with-main", "lib", "entry.js"));
  });

  it("rejects with ModuleNotFoundError for a missing specifier", async () => {
    await expect(
      resolveModuleAsync("does-not-exist", { basedir: fixtures }),
    ).rejects.toThrow(ModuleNotFoundError);
  });
});

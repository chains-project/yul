import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { ModuleNotFoundError, createResolver } from "../dist/index.js";

const fixtures = path.join(path.dirname(fileURLToPath(import.meta.url)), "fixtures");
const appDir = path.join(fixtures, "app", "src");

test("resolves a bare specifier through package.json main", async () => {
  const resolver = createResolver();
  const result = await resolver.resolve("greeting", { basedir: appDir });
  assert.equal(result, path.join(fixtures, "node_modules", "greeting", "lib", "main.js"));
});

test("resolves relative specifiers with and without extensions", async () => {
  const resolver = createResolver();
  assert.equal(
    await resolver.resolve("./sibling.js", { basedir: appDir }),
    path.join(appDir, "sibling.js"),
  );
  assert.equal(
    await resolver.resolve("./sibling", { basedir: appDir }),
    path.join(appDir, "sibling.js"),
  );
});

test("honors package.json exports conditions", async () => {
  const requireResolver = createResolver({ conditionNames: ["node", "require", "default"] });
  const importResolver = createResolver({ conditionNames: ["node", "import", "default"] });

  assert.equal(
    await requireResolver.resolve("with-exports", { basedir: appDir }),
    path.join(fixtures, "node_modules", "with-exports", "cjs", "index.js"),
  );
  assert.equal(
    await importResolver.resolve("with-exports", { basedir: appDir }),
    path.join(fixtures, "node_modules", "with-exports", "esm", "index.js"),
  );
});

test("resolves exports subpaths", async () => {
  const resolver = createResolver();
  assert.equal(
    await resolver.resolve("with-exports/feature", { basedir: appDir }),
    path.join(fixtures, "node_modules", "with-exports", "feature.js"),
  );
});

test("returns core modules unchanged", async () => {
  const resolver = createResolver();
  assert.equal(await resolver.resolve("node:fs"), "node:fs");
  assert.equal(await resolver.resolve("path"), "path");
});

test("resolveSync matches resolve", async () => {
  const resolver = createResolver();
  const sync = resolver.resolveSync("greeting", { basedir: appDir });
  const asyncResult = await resolver.resolve("greeting", { basedir: appDir });
  assert.equal(sync, asyncResult);
});

test("applies aliases", async () => {
  const resolver = createResolver({
    alias: { "@sibling": path.join(appDir, "sibling.js") },
  });
  assert.equal(
    await resolver.resolve("@sibling", { basedir: appDir }),
    path.join(appDir, "sibling.js"),
  );
});

test("throws MODULE_NOT_FOUND for unknown specifiers", async () => {
  const resolver = createResolver();
  await assert.rejects(
    () => resolver.resolve("does-not-exist", { basedir: appDir }),
    (err) => {
      assert.ok(err instanceof ModuleNotFoundError);
      assert.equal(err.code, "MODULE_NOT_FOUND");
      assert.equal(err.specifier, "does-not-exist");
      return true;
    },
  );
  assert.throws(
    () => resolver.resolveSync("does-not-exist", { basedir: appDir }),
    (err) => err instanceof ModuleNotFoundError && err.code === "MODULE_NOT_FOUND",
  );
});

import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, symlink, writeFile } from "node:fs/promises";
import { realpathSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { resolveRealPath, resolveRealPathSync } from "../src/index.js";

test("resolves a symlinked file to its target", async () => {
  const dir = await mkdtemp(join(tmpdir(), "realpath-"));
  const target = join(dir, "target.txt");
  const link = join(dir, "link.txt");
  await writeFile(target, "hello");
  await symlink(target, link);

  assert.equal(await resolveRealPath(link), await resolveRealPath(target));
  assert.equal(resolveRealPathSync(link), realpathSync(target));
});

test("resolves symlinked directories", async () => {
  const dir = await mkdtemp(join(tmpdir(), "realpath-"));
  const targetDir = join(dir, "real");
  const linkDir = join(dir, "link");
  await mkdir(targetDir);
  await symlink(targetDir, linkDir);

  assert.equal(await resolveRealPath(linkDir), await resolveRealPath(targetDir));
});

test("rejects on missing paths", async () => {
  await assert.rejects(resolveRealPath("/no/such/path/here"));
});

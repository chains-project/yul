#!/usr/bin/env node
import { watch } from "chokidar";
import { resolve } from "node:path";

const target = resolve(process.argv[2] ?? process.cwd());

const watcher = watch(target, {
  persistent: true,
  ignoreInitial: false,
  awaitWriteFinish: { stabilityThreshold: 100, pollInterval: 25 },
});

const log = (event, path) =>
  console.log(`${new Date().toISOString()} ${event.padEnd(10)} ${path}`);

watcher
  .on("add", (path) => log("add", path))
  .on("addDir", (path) => log("addDir", path))
  .on("change", (path) => log("change", path))
  .on("unlink", (path) => log("unlink", path))
  .on("unlinkDir", (path) => log("unlinkDir", path))
  .on("error", (error) => console.error(`watch error: ${error.message}`))
  .on("ready", () =>
    console.log(`watching ${target} (native FSEvents backend on macOS)`),
  );

const shutdown = () => {
  watcher.close().then(() => process.exit(0));
};
process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

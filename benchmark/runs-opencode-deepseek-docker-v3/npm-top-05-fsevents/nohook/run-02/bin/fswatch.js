#!/usr/bin/env node
import process from "node:process";
import { watch } from "../src/index.js";

function parseArgs(argv) {
  const options = { json: false, native: false, latency: 0.25, targets: [] };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];

    if (arg === "-h" || arg === "--help") {
      options.help = true;
    } else if (arg === "--json") {
      options.json = true;
    } else if (arg === "--native") {
      options.native = true;
    } else if (arg === "--latency") {
      options.latency = Number(argv[(i += 1)]);
    } else if (arg.startsWith("--latency=")) {
      options.latency = Number(arg.slice("--latency=".length));
    } else if (arg.startsWith("-")) {
      options.unknown = arg;
    } else {
      options.targets.push(arg);
    }
  }

  return options;
}

function usage() {
  return [
    "Usage: fswatch-native [options] <path...>",
    "",
    "Options:",
    "  --json           emit newline-delimited JSON events",
    "  --native         require the native fsevents backend",
    "  --latency <sec>  FSEvents coalescing latency (default 0.25)",
    "  -h, --help       show this help",
  ].join("\n");
}

const options = parseArgs(process.argv.slice(2));

if (options.help) {
  console.log(usage());
  process.exit(0);
}

if (options.unknown) {
  console.error(`unknown option: ${options.unknown}\n`);
  console.error(usage());
  process.exit(2);
}

if (options.targets.length === 0) {
  console.error("at least one path is required\n");
  console.error(usage());
  process.exit(2);
}

const watcher = await watch(options.targets, options);

watcher.on("error", (err) => {
  console.error(`watch error: ${err.message}`);
});

watcher.on("event", (event) => {
  if (options.json) {
    console.log(JSON.stringify(event));
    return;
  }

  const stamp = new Date().toISOString();
  console.log(`${stamp} ${event.event.padEnd(12)} ${event.type.padEnd(7)} ${event.path}`);
});

process.on("SIGINT", () => {
  watcher.close();
  process.exit(0);
});

process.on("SIGTERM", () => {
  watcher.close();
  process.exit(0);
});

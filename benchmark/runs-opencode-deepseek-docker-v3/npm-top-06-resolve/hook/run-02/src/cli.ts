#!/usr/bin/env node
import process from "node:process";
import { resolve, ResolveError, type ResolveOptions } from "./resolver.js";

interface CliResult {
  options: ResolveOptions;
  request?: string;
}

function printHelp(): void {
  process.stdout.write(
    [
      "Usage: resolve-module <specifier> [options]",
      "",
      "Programmatically resolves a module specifier using Node.js's",
      "CommonJS resolution algorithm.",
      "",
      "Options:",
      "  -b, --basedir <dir>       Directory to resolve from (default: cwd)",
      "  -c, --conditions <list>   Comma separated export conditions",
      "  -e, --extensions <list>   Comma separated file extensions",
      "      --preserve-symlinks   Do not dereference symlinks",
      "      --no-core-modules     Reject built-in modules",
      "  -h, --help                Show this help",
      "",
    ].join("\n")
  );
}

function parseArgs(argv: string[]): CliResult {
  const options: ResolveOptions = {};
  let request: string | undefined;

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    switch (arg) {
      case "-b":
      case "--basedir":
        options.basedir = argv[++i];
        break;
      case "-c":
      case "--conditions":
        options.conditions = (argv[++i] ?? "").split(",").filter(Boolean);
        break;
      case "-e":
      case "--extensions":
        options.extensions = (argv[++i] ?? "").split(",").filter(Boolean);
        break;
      case "--preserve-symlinks":
        options.preserveSymlinks = true;
        break;
      case "--no-core-modules":
        options.includeCoreModules = false;
        break;
      case "-h":
      case "--help":
        printHelp();
        process.exit(0);
        break;
      default:
        request = arg;
    }
  }

  return { options, request };
}

const { options, request } = parseArgs(process.argv.slice(2));

if (request === undefined) {
  printHelp();
  process.exit(1);
}

try {
  process.stdout.write(`${resolve(request, options)}\n`);
} catch (error) {
  if (error instanceof ResolveError) {
    process.stderr.write(`${error.code}: ${error.message}\n`);
    process.exit(1);
  }
  throw error;
}

import { createRequire } from "node:module";
import { statSync } from "node:fs";
import path from "node:path";

function toRequireBase(from) {
  const resolved = path.resolve(from);

  let stats;
  try {
    stats = statSync(resolved);
  } catch {
    return path.join(resolved, "index.js");
  }

  return stats.isDirectory() ? path.join(resolved, "index.js") : resolved;
}

export function createResolver(defaults = {}) {
  return function resolve(specifier, options = {}) {
    if (typeof specifier !== "string" || specifier.length === 0) {
      throw new TypeError("specifier must be a non-empty string");
    }

    const { from, paths } = { ...defaults, ...options };
    const base = from ?? process.cwd();
    const require = createRequire(toRequireBase(base));

    return require.resolve(specifier, paths ? { paths } : undefined);
  };
}

export const resolve = createResolver();

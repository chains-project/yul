import { readFileSync } from "node:fs";
import { dirname, join, parse } from "node:path";

export interface PackageJson {
  name?: string;
  main?: string;
  exports?: unknown;
  imports?: unknown;
  type?: "module" | "commonjs";
}

export interface PackageInfo {
  dir: string;
  data: PackageJson;
}

const cache = new Map<string, PackageInfo | null>();

export function readPackage(dir: string): PackageInfo | undefined {
  const cached = cache.get(dir);
  if (cached !== undefined) return cached ?? undefined;

  const file = join(dir, "package.json");
  let info: PackageInfo | undefined;
  try {
    const raw = readFileSync(file, "utf8");
    info = { dir, data: JSON.parse(raw) as PackageJson };
  } catch {
    info = undefined;
  }

  cache.set(dir, info ?? null);
  return info;
}

export function findNearestPackage(start: string): PackageInfo | undefined {
  let current = start;
  const { root } = parse(current);
  for (;;) {
    const info = readPackage(current);
    if (info) return info;
    if (current === root) return undefined;
    current = dirname(current);
  }
}

export function clearPackageCache(): void {
  cache.clear();
}

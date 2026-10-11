import type { PackageJson } from "./package-json.js";

type Target = string | null | Target[] | { [key: string]: Target };

function isConditionObject(value: object): boolean {
  return !Object.keys(value).some((key) => key.startsWith("."));
}

function substitute(target: string, pattern: string | undefined): string {
  return pattern === undefined ? target : target.replaceAll("*", pattern);
}

function resolveTarget(
  target: Target,
  conditions: readonly string[],
  pattern?: string,
): string | undefined {
  if (target === null) return undefined;
  if (typeof target === "string") return substitute(target, pattern);
  if (Array.isArray(target)) {
    for (const item of target) {
      const resolved = resolveTarget(item, conditions, pattern);
      if (resolved !== undefined) return resolved;
    }
    return undefined;
  }
  if (typeof target === "object") {
    for (const [condition, value] of Object.entries(target)) {
      if (condition === "default" || conditions.includes(condition)) {
        const resolved = resolveTarget(value as Target, conditions, pattern);
        if (resolved !== undefined) return resolved;
      }
    }
  }
  return undefined;
}

function patternMatch(key: string, subpath: string): string | undefined {
  const star = key.indexOf("*");
  if (star === -1) return undefined;
  const prefix = key.slice(0, star);
  const suffix = key.slice(star + 1);
  if (
    subpath.length < prefix.length + suffix.length ||
    !subpath.startsWith(prefix) ||
    !subpath.endsWith(suffix)
  ) {
    return undefined;
  }
  return subpath.slice(prefix.length, subpath.length - suffix.length);
}

function resolveMap(
  map: Record<string, Target>,
  subpath: string,
  conditions: readonly string[],
): string | undefined {
  const exact = map[subpath];
  if (exact !== undefined) return resolveTarget(exact, conditions);

  const patterns = Object.keys(map)
    .filter((key) => key.includes("*"))
    .sort((a, b) => b.indexOf("*") - a.indexOf("*"));

  for (const key of patterns) {
    const pattern = patternMatch(key, subpath);
    if (pattern !== undefined) {
      const resolved = resolveTarget(map[key] as Target, conditions, pattern);
      if (resolved !== undefined) return resolved;
    }
  }
  return undefined;
}

function subpathOf(specifier: string, packageName: string): string {
  const rest = specifier.slice(packageName.length);
  return rest === "" ? "." : `.${rest}`;
}

export function splitPackageSpecifier(
  specifier: string,
): { name: string; subpath: string } | undefined {
  const parts = specifier.split("/");
  if (specifier.startsWith("@")) {
    if (parts.length < 2) return undefined;
    const name = `${parts[0]}/${parts[1]}`;
    return { name, subpath: subpathOf(specifier, name) };
  }
  const name = parts[0];
  if (!name) return undefined;
  return { name, subpath: subpathOf(specifier, name) };
}

export function resolveExports(
  pkg: PackageJson,
  subpath: string,
  conditions: readonly string[],
): string | undefined {
  const { exports } = pkg;
  if (exports === undefined) return undefined;

  if (typeof exports === "string" || exports === null || Array.isArray(exports)) {
    return subpath === "." ? resolveTarget(exports as Target, conditions) : undefined;
  }

  if (typeof exports === "object") {
    const map = exports as Record<string, Target>;
    if (isConditionObject(map)) {
      return subpath === "." ? resolveTarget(map, conditions) : undefined;
    }
    return resolveMap(map, subpath, conditions);
  }
  return undefined;
}

export function resolveImports(
  pkg: PackageJson,
  specifier: string,
  conditions: readonly string[],
): string | undefined {
  const { imports } = pkg;
  if (imports === undefined || typeof imports !== "object" || imports === null) {
    return undefined;
  }
  return resolveMap(imports as Record<string, Target>, specifier, conditions);
}

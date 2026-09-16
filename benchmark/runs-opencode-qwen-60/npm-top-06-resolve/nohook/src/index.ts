import { ResolveOptions } from "./types.js";
import { Resolver } from "./resolver.js";

export function createResolver(options: ResolveOptions = {}): Resolver {
  return new Resolver(options);
}

export { Resolver } from "./resolver.js";
export type { ResolveOptions, ResolveResult, ResolveError } from "./types.js";
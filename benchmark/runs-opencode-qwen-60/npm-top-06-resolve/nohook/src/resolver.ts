import { resolve as pathResolve, dirname, join, extname, basename } from "path";
import { readFileSync, existsSync, lstatSync } from "fs";
import { ResolveOptions, ResolveResult, ResolveError } from "./types.js";

export class Resolver {
  private baseUrl: string;
  private paths: Record<string, string[]>;
  private extensions: string[];
  private mainFields: string[];
  private conditionNames: string[];
  private preserveSymlinks: boolean;

  constructor(options: ResolveOptions = {}) {
    this.baseUrl = options.baseUrl ?? process.cwd();
    this.paths = options.paths ?? {};
    this.extensions = options.extensions ?? [".js", ".json", ".node"];
    this.mainFields = options.mainFields ?? ["main"];
    this.conditionNames = options.conditionNames ?? ["require", "default"];
    this.preserveSymlinks = options.preserveSymlinks ?? false;
  }

  resolve(request: string, containingDir?: string): ResolveResult {
    const baseDir = containingDir ?? this.baseUrl;

    if (request.startsWith("node:")) {
      const core = request.replace(/^node:/, "");
      const builtins = [
        "assert", "async_hooks", "buffer", "child_process", "cluster",
        "console", "constants", "crypto", "dgram", "diagnostics_channel",
        "dns", "domain", "events", "fs", "http", "http2", "https",
        "inspector", "module", "net", "os", "path", "perf_hooks",
        "process", "punycode", "querystring", "readline", "repl",
        "stream", "string_decoder", "sys", "timers", "tls", "trace_events",
        "tty", "url", "util", "v8", "vm", "wasi", "worker_threads", "zlib"
      ];
      if (builtins.includes(core)) {
        throw new ResolveError("MODULE_NOT_FOUND", `Cannot find module '${request}'`, request, baseDir);
      }
    }

    if (isAbsolute(request)) {
      return this.resolveFromAbsolute(request, baseDir);
    }

    if (request.startsWith(".")) {
      return this.resolveRelative(request, baseDir);
    }

    return this.resolveModule(request, baseDir);
  }

  private resolveFromAbsolute(request: string, _baseDir: string): ResolveResult {
    if (existsSync(request) && lstatSync(request).isDirectory()) {
      return this.resolvePackageRoot(request);
    }

    for (const ext of this.extensions) {
      const target = request.endsWith(ext) ? request : request + ext;
      if (existsSync(target)) {
        return { path: this.resolveSymlinks(target) };
      }
    }

    throw new ResolveError("MODULE_NOT_FOUND", `Cannot find module '${request}' from '${_baseDir}'`, request, _baseDir);
  }

  private resolveRelative(request: string, baseDir: string): ResolveResult {
    const resolved = pathResolve(baseDir, request);

    if (existsSync(resolved) && lstatSync(resolved).isDirectory()) {
      return this.resolvePackageRoot(resolved);
    }

    if (existsSync(resolved)) {
      return { path: this.resolveSymlinks(resolved) };
    }

    for (const ext of this.extensions) {
      const target = resolved.endsWith(ext) ? resolved : resolved + ext;
      if (existsSync(target)) {
        return { path: this.resolveSymlinks(target) };
      }
    }

    throw new ResolveError("MODULE_NOT_FOUND", `Cannot find module '${request}' from '${baseDir}'`, request, baseDir);
  }

  private resolveModule(request: string, baseDir: string): ResolveResult {
    const packagesDir = pathResolve(baseDir, "node_modules");
    
    if (!existsSync(packagesDir)) {
      throw new ResolveError("MODULE_NOT_FOUND", `Cannot find module '${request}' from '${baseDir}'`, request, baseDir);
    }

    if (this.paths[request]) {
      for (const candidate of this.paths[request]) {
        const resolved = pathResolve(baseDir, candidate);
        if (existsSync(resolved)) {
          if (lstatSync(resolved).isDirectory()) {
            return this.resolvePackageRoot(resolved);
          }
          return { path: this.resolveSymlinks(resolved) };
        }
      }
    }

    let currentDir = baseDir;
    while (currentDir !== pathResolve(currentDir, "..")) {
      const moduleDir = pathResolve(currentDir, "node_modules", request);
      
      if (existsSync(moduleDir)) {
        if (lstatSync(moduleDir).isDirectory()) {
          return this.resolvePackageRoot(moduleDir);
        }
        return { path: this.resolveSymlinks(moduleDir) };
      }

      const indexDir = pathResolve(currentDir, "node_modules", request, "index");
      for (const ext of this.extensions) {
        const target = indexDir + ext;
        if (existsSync(target)) {
          return { path: this.resolveSymlinks(target) };
        }
      }

      currentDir = pathResolve(currentDir, "..");
    }

    throw new ResolveError("MODULE_NOT_FOUND", `Cannot find module '${request}' from '${baseDir}'`, request, baseDir);
  }

  private resolvePackageRoot(pkgDir: string): ResolveResult {
    const packageJsonPath = pathResolve(pkgDir, "package.json");
    let packageJson: ResolveResult["packageJson"];
    let packageType: ResolveResult["packageType"] = "commonjs";

    if (existsSync(packageJsonPath)) {
      packageJson = JSON.parse(readFileSync(packageJsonPath, "utf-8"));

      if (packageJson.type === "module") {
        packageType = "module";
      }
    }

    const mainField = this.mainFields.find(f => packageJson?.[f]);
    const main = mainField ? (packageJson?.[mainField] as string) : "index.js";

    if (main) {
      const resolvedMain = pathResolve(pkgDir, main);
      if (existsSync(resolvedMain)) {
        return { path: this.resolveSymlinks(resolvedMain), packageJson, packageType };
      }

      for (const ext of this.extensions) {
        const target = resolvedMain + ext;
        if (existsSync(target)) {
          return { path: this.resolveSymlinks(target), packageJson, packageType };
        }
      }
    }

    return { path: this.resolveSymlinks(pkgDir), packageJson, packageType };
  }

  private resolveSymlinks(filePath: string): string {
    if (this.preserveSymlinks) {
      return filePath;
    }

    if (existsSync(filePath) && lstatSync(filePath).isSymbolicLink()) {
      const realPath = readFileSync(filePath, "utf-8").trim();
      if (realPath.startsWith(".")) {
        return this.resolveSymlinks(pathResolve(dirname(filePath), realPath));
      }
      return this.resolveSymlinks(realPath);
    }

    return filePath;
  }
}

function isAbsolute(request: string): boolean {
  return request.startsWith("/") || /^[a-zA-Z]:/.test(request);
}
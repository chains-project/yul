export interface ResolveOptions {
  baseUrl?: string;
  paths?: Record<string, string[]>;
  extensions?: string[];
  mainFields?: string[];
  conditionNames?: string[];
  preserveSymlinks?: boolean;
}

export interface ResolveResult {
  path: string;
  packageJson?: {
    name?: string;
    version?: string;
    type?: string;
    exports?: Record<string, unknown> | string[] | string;
    main?: string;
    imports?: Record<string, unknown>;
  };
  packageType?: "commonjs" | "module";
}

export class ResolveError extends Error {
  public readonly code: string;
  public readonly request: string;
  public readonly containingDir: string;

  constructor(code: string, message: string, request: string, containingDir: string) {
    super(message);
    this.name = "ResolveError";
    this.code = code;
    this.request = request;
    this.containingDir = containingDir;
  }
}

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
    
    if (isAbsolute(request)) {
      return this.resolveFromAbsolute(request, baseDir);
    }

    if (request.startsWith(".")) {
      return this.resolveRelative(request, baseDir);
    }

    return this.resolveModule(request, baseDir);
  }
}

function isAbsolute(request: string): boolean {
  return request.startsWith("/") || /^[a-zA-Z]:/.test(request);
}

function isBuiltinModule(request: string): boolean {
  const builtins = [
    "assert", "async_hooks", "buffer", "child_process", "cluster",
    "console", "constants", "crypto", "dgram", "diagnostics_channel",
    "dns", "domain", "events", "fs", "http", "http2", "https",
    "inspector", "module", "net", "os", "path", "perf_hooks",
    "process", "punycode", "querystring", "readline", "repl",
    "stream", "string_decoder", "sys", "timers", "tls", "trace_events",
    "tty", "url", "util", "v8", "vm", "wasi", "worker_threads", "zlib"
  ];
  const core = request.replace(/^node:/, "");
  return builtins.includes(core);
}
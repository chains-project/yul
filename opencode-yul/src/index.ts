// yul OpenCode plugin: keeps dependencies current by blocking `write`/`edit`
// tool calls that would pin a newly added/changed dependency to a version
// older than what's actually released.
//
// Distributed as the npm package "opencode-yul" — add it to the `plugin`
// array in your project's opencode.json/opencode.jsonc:
//
//   { "plugin": ["opencode-yul"] }
//
// NOTE: `input.tool` values and `output.args` field names below were
// confirmed against the built-in write/edit tool schemas in opencode-ai@1.18.31
// (write: {content, filePath}; edit: {filePath, oldString, newString, replaceAll}).
// Re-check if the hook stops firing after an OpenCode upgrade changes these.

import type { Plugin } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"
import { existsSync, mkdirSync, readdirSync, rmSync } from "node:fs"
import { homedir } from "node:os"
import { join } from "node:path"

// Bump this alongside the `version` in .claude-plugin/plugin.json (and this
// package's own package.json version) on every release — it's what pins
// which yul binary this plugin downloads and runs.
const YUL_VERSION = "0.0.12"

const CACHE_ROOT = join(process.env.XDG_CACHE_HOME ?? join(homedir(), ".cache"), "yul")
const CACHE_DIR = join(CACHE_ROOT, `v${YUL_VERSION}`)
const BIN_PATH = join(CACHE_DIR, "yul")

// ensureYul downloads the pinned yul release binary into the cache dir if
// it isn't already there, then prunes caches left behind by other versions.
// Mirrors scripts/ensure-yul.sh, minus the "newer release available"
// notice, which has no obvious OpenCode-side equivalent to print to.
function ensureYul(): void {
	if (existsSync(BIN_PATH)) return

	mkdirSync(CACHE_DIR, { recursive: true })
	const result = spawnSync("sh", ["-c", `curl -fsSL "https://raw.githubusercontent.com/chains-project/yul/v${YUL_VERSION}/install.sh" | sh`], {
		env: { ...process.env, YUL_VERSION: `v${YUL_VERSION}`, YUL_INSTALL_DIR: CACHE_DIR },
		stdio: "ignore",
	})
	if (result.status !== 0 || !existsSync(BIN_PATH)) return // fail open: hook below no-ops until the binary exists

	if (existsSync(CACHE_ROOT)) {
		for (const entry of readdirSync(CACHE_ROOT, { withFileTypes: true })) {
			if (entry.isDirectory() && entry.name.startsWith("v") && entry.name !== `v${YUL_VERSION}`) {
				rmSync(join(CACHE_ROOT, entry.name), { recursive: true, force: true })
			}
		}
	}
}

// hookInput mirrors the JSON shape yul's PreToolUse hook already parses
// (see hookInput in main.go), so this plugin can drive the same binary
// unmodified regardless of which agent host it's running under.
type hookInput = {
	tool_name: "Write" | "Edit"
	tool_input: {
		file_path: string
		content?: string
		old_string?: string
		new_string?: string
		replace_all?: boolean
	}
}

function toHookInput(tool: string, args: any): hookInput | undefined {
	if (tool === "write") {
		return { tool_name: "Write", tool_input: { file_path: args.filePath, content: args.content } }
	}
	if (tool === "edit") {
		return {
			tool_name: "Edit",
			tool_input: {
				file_path: args.filePath,
				old_string: args.oldString,
				new_string: args.newString,
				replace_all: args.replaceAll,
			},
		}
	}
	return undefined
}

export const Yul: Plugin = async () => {
	ensureYul()

	return {
		"tool.execute.before": async (input, output) => {
			if (!existsSync(BIN_PATH)) return // fail open: still downloading, or offline install

			const hookInput = toHookInput(input.tool, output.args)
			if (!hookInput) return

			const result = spawnSync(BIN_PATH, [], {
				input: JSON.stringify(hookInput),
				encoding: "utf8",
			})

			if (result.status === 2) {
				throw new Error(result.stderr || "yul: dependency pin is outdated")
			}
			// any other exit code (0, or a resolver/plumbing error) fails open
		},
	}
}

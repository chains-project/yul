package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/chains-project/yul/pkg/githubactions"
	"github.com/chains-project/yul/pkg/maven"
	"github.com/chains-project/yul/pkg/npm"
	"github.com/chains-project/yul/pkg/pypi"
	"github.com/chains-project/yul/pkg/scan"
	"github.com/chains-project/yul/pkg/util/manifestchecker"
	"github.com/chains-project/yul/pkg/util/resolver"
)

// newCheckers builds the registry of manifest checkers the hook dispatches
// to, keyed off which manifest filename each one owns. Add an entry here as
// each ecosystem's checker is implemented. res is shared across the
// checkers that resolve latest versions through git-pkgs/enrichment.
func newCheckers(res resolver.Resolver) []manifestchecker.ManifestChecker {
	return []manifestchecker.ManifestChecker{
		maven.Checker{Resolver: res},
		pypi.RequirementsChecker{Resolver: res},
		pypi.PyprojectChecker{Resolver: res},
		npm.Checker{Resolver: res},
		githubactions.Checker{Resolver: res},
	}
}

// checkerFor finds the checker that owns path, the file as passed to the
// hook (typically absolute). Most checkers claim a fixed basename; a
// checker that instead implements manifestchecker.PathMatcher (e.g.
// githubactions, whose workflow files have arbitrary basenames) is tried
// first against the full path.
func checkerFor(checkers []manifestchecker.ManifestChecker, path string) manifestchecker.ManifestChecker {
	base := filepath.Base(path)
	for _, c := range checkers {
		if pm, ok := c.(manifestchecker.PathMatcher); ok {
			if pm.MatchesPath(path) {
				return c
			}
			continue
		}
		if c.Filename() == base {
			return c
		}
	}
	return nil
}

// version is set at build time via -ldflags "-X main.version=..." (see
// .goreleaser.yml); it stays "dev" for `go build`/`go run`.
var version = "dev"

// hookInput is the subset of Claude Code's PreToolUse hook payload we need.
type hookInput struct {
	ToolName  string `json:"tool_name"`
	ToolInput struct {
		FilePath   string `json:"file_path"`
		Content    string `json:"content"`     // Write
		OldString  string `json:"old_string"`  // Edit
		NewString  string `json:"new_string"`  // Edit
		ReplaceAll bool   `json:"replace_all"` // Edit
	} `json:"tool_input"`
}

// runHook is a PreToolUse hook for the Write and Edit tools. It figures out
// which ecosystem owns the manifest being written (by filename), and blocks
// (exit 2) if a newly added/changed dependency is pinned older than what's
// actually released. Claude sees the block reason on stderr and can retry.
func runHook() {
	raw, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintf(os.Stderr, "hook: reading stdin: %v\n", err)
		os.Exit(0) // fail open: don't block Claude on a hook plumbing error
	}

	var in hookInput
	if err := json.Unmarshal(raw, &in); err != nil {
		fmt.Fprintf(os.Stderr, "hook: parsing hook payload: %v\n", err)
		os.Exit(0)
	}

	if in.ToolName != "Write" && in.ToolName != "Edit" {
		os.Exit(0)
	}

	res, err := resolver.NewEnrichmentResolver()
	if err != nil {
		fmt.Fprintf(os.Stderr, "hook: creating resolver: %v\n", err)
		os.Exit(0) // fail open: a resolver construction error shouldn't block the write
	}

	checker := checkerFor(newCheckers(res), in.ToolInput.FilePath)
	if checker == nil {
		// manifest not known
		os.Exit(0)
	}

	rawBefore, err := os.ReadFile(in.ToolInput.FilePath)
	if err != nil {
		rawBefore = nil // file doesn't exist yet: every dependency in it is new
	}
	before := string(rawBefore)

	after := in.ToolInput.Content
	if in.ToolName == "Edit" {
		if !strings.Contains(before, in.ToolInput.OldString) {
			// Edit tool itself would fail on this; nothing for us to check.
			os.Exit(0)
		}
		count := 1
		if in.ToolInput.ReplaceAll {
			count = -1
		}
		after = strings.Replace(before, in.ToolInput.OldString, in.ToolInput.NewString, count)
	}

	mismatches, err := checker.Check(before, after)
	if err != nil {
		fmt.Fprintf(os.Stderr, "hook: %v\n", err)
		os.Exit(0) // fail open: a resolver/network error shouldn't block the write
	}

	if len(mismatches) == 0 {
		os.Exit(0)
	}

	fmt.Fprintln(os.Stderr, "outdated dependencies, use these versions instead:")
	for _, m := range mismatches {
		name := m.Name
		if m.Namespace != "" {
			name = m.Namespace + ":" + m.Name
		}
		fmt.Fprintf(os.Stderr, "  %s  %s -> %s\n", name, m.Current, m.Latest)
	}
	os.Exit(2)
}

// scanCacheTTL is how long a project scan's cached findings are reused
// before session-scan.sh triggers a fresh one. A yul upgrade always forces
// a rescan regardless of TTL (see scan.Cache.Fresh), since a newer build
// may parse or resolve differently.
const scanCacheTTL = time.Hour * 24 * 7

// sessionStartInput is the subset of Claude Code's SessionStart hook
// payload we need, read from stdin when --project-dir isn't passed.
type sessionStartInput struct {
	CWD string `json:"cwd"`
}

// runScan is a SessionStart hook for the "scan" subcommand. It walks the
// project for every exactly-pinned dependency across all known manifest
// kinds (not just ones a Write/Edit just touched), reusing a cached result
// up to scanCacheTTL old, and emits any findings as additionalContext so
// Claude can ask the user whether to update them. It never blocks session
// startup: any failure here just means no context gets added.
func runScan(args []string) {
	fset := flag.NewFlagSet("scan", flag.ContinueOnError)
	fset.SetOutput(io.Discard)
	projectDir := fset.String("project-dir", "", "project directory to scan (default: SessionStart hook's cwd, or $PWD)")
	if err := fset.Parse(args); err != nil {
		os.Exit(0)
	}

	dir := *projectDir
	if dir == "" {
		if raw, err := io.ReadAll(os.Stdin); err == nil {
			var in sessionStartInput
			if json.Unmarshal(raw, &in) == nil {
				dir = in.CWD
			}
		}
	}
	if dir == "" {
		var err error
		dir, err = os.Getwd()
		if err != nil {
			os.Exit(0)
		}
	}

	cacheHome := os.Getenv("XDG_CACHE_HOME")
	if cacheHome == "" {
		home, err := os.UserHomeDir()
		if err != nil {
			os.Exit(0)
		}
		cacheHome = filepath.Join(home, ".cache")
	}

	cachePath, err := scan.CachePath(cacheHome, dir)
	if err != nil {
		os.Exit(0)
	}

	// Matching checkers (Filename/MatchesPath) needs no resolver, so this
	// hash is network-free and cheap enough to compute on every session
	// start, unlike a full rescan.
	matchers := newCheckers(nil)
	hash, err := scan.Hash(dir, matchers)
	if err != nil {
		os.Exit(0)
	}

	now := time.Now()
	if cached, ok := scan.LoadCache(cachePath); ok && cached.Fresh(version, scanCacheTTL, now, hash) {
		emitScanContext(cached.Findings, cached.ScannedAt)
		return
	}

	res, err := resolver.NewEnrichmentResolver()
	if err != nil {
		os.Exit(0) // fail open: don't add context, don't block startup
	}

	findings, err := scan.Dir(dir, newCheckers(res))
	if err != nil {
		os.Exit(0)
	}

	// Cache the result even if it's empty, so a clean project doesn't get
	// re-resolved every session either.
	_ = scan.SaveCache(cachePath, scan.Cache{
		YulVersion:    version,
		ManifestsHash: hash,
		ScannedAt:     now,
		ProjectDir:    dir,
		Findings:      findings,
	})

	emitScanContext(findings, now)
}

// emitScanContext prints the SessionStart hook JSON that adds findings to
// Claude's context, or nothing if there's nothing to report.
func emitScanContext(findings []scan.Finding, scannedAt time.Time) {
	if len(findings) == 0 {
		os.Exit(0)
	}

	var b strings.Builder
	fmt.Fprintf(&b, "yul scanned this project's manifests (as of %s) and found %d pinned dependencies older than the latest release:\n",
		scannedAt.Format("2006-01-02"), len(findings))
	for _, f := range findings {
		name := f.Name
		if f.Namespace != "" {
			name = f.Namespace + ":" + f.Name
		}
		fmt.Fprintf(&b, "  %s: %s  %s -> %s\n", f.File, name, f.Current, f.Latest)
	}
	b.WriteString("Ask the user whether they'd like these updated before making any other changes to these files.")

	out := struct {
		HookSpecificOutput struct {
			HookEventName     string `json:"hookEventName"`
			AdditionalContext string `json:"additionalContext"`
		} `json:"hookSpecificOutput"`
	}{}
	out.HookSpecificOutput.HookEventName = "SessionStart"
	out.HookSpecificOutput.AdditionalContext = b.String()

	raw, err := json.Marshal(out)
	if err != nil {
		os.Exit(0)
	}
	os.Stdout.Write(raw)
	os.Exit(0)
}

func main() {
	if len(os.Args) > 1 {
		switch os.Args[1] {
		case "version":
			fmt.Println(version)
			return
		case "scan":
			runScan(os.Args[2:])
			return
		}
	}
	runHook()
}

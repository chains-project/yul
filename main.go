package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	"github.com/git-pkgs/purl"

	"github.com/chains-project/yul/pkg/cargo"
	"github.com/chains-project/yul/pkg/githubactions"
	"github.com/chains-project/yul/pkg/golang"
	"github.com/chains-project/yul/pkg/maven"
	"github.com/chains-project/yul/pkg/npm"
	"github.com/chains-project/yul/pkg/pypi"
	"github.com/chains-project/yul/pkg/scan"
	"github.com/chains-project/yul/pkg/util/manifestchecker"
	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/chains-project/yul/pkg/util/pins"
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
		githubactions.Checker{Resolver: res, Sha: githubactions.EcosystemsShaResolver{}},
		golang.Checker{Resolver: res},
		cargo.Checker{Resolver: res},
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
		Command    string `json:"command"`     // Bash
	} `json:"tool_input"`
}

const manifestNamesRE = `(?:pom\.xml|requirements\.txt|pyproject\.toml|package\.json|go\.mod|Cargo\.toml|\.github/workflows/[^\s'"]+\.ya?ml)`

// clause bounds the gap between a write construct's keyword (e.g. `tee`)
// and the manifest name that must be its own target argument, so e.g.
// `tee notes.txt; cat package.json` doesn't match: the `;` before
// package.json stops the gap, since tee's real target is notes.txt, not the
// manifest.
const clause = `[^;&|\n]`

// writeConstructToManifestRE matches shell constructs that mutate a file's
// content, other than `>`/`>>` (handled by redirectToManifestRE), where the
// manifest name is the construct's own target argument.
var writeConstructToManifestRE = regexp.MustCompile(
	`\btee\b` + clause + `*` + manifestNamesRE +
		`|\b(?:sed|perl)\s+-i\b` + clause + `*` + manifestNamesRE +
		`|\bdd\b` + clause + `*?\bof=['"]?(?:[^\s'"]*/)?` + manifestNamesRE +
		`|\b(?:cp|mv)\s+` + clause + `*` + manifestNamesRE,
)

// redirectToManifestRE matches a `>`/`>>` whose target is a known manifest
// name, e.g. `cat > pom.xml <<EOF`, `echo "foo==1.0" >> requirements.txt`.
// Excludes fd duplication like `2>&1` and unrelated redirects like `2>/dev/null`
// by requiring the manifest name immediately after the operator, rather
// than just matching any `>` present elsewhere in cmd.
var redirectToManifestRE = regexp.MustCompile(`>>?\s*['"]?(?:[^\s'"]*/)?` + manifestNamesRE + `['"]?(\s|;|&|\||$)`)

// looksLikeManifestWrite reports whether cmd looks like it rewrites a known
// manifest's content directly, bypassing the Write/Edit path runHook checks.
func looksLikeManifestWrite(cmd string) bool {
	return writeConstructToManifestRE.MatchString(cmd) || redirectToManifestRE.MatchString(cmd)
}

// pkgManagerPinPatterns matches a package manager's own CLI syntax for
// pinning a dependency to an exact version, e.g. `go get mod@v1.2.3`,
// `npm install pkg@1.2.3`, `pip install pkg==1.2.3`, `cargo add crate@1.2.3`
// - these write the manifest just as much as a redirect does, but don't
// match looksLikeManifestWrite's direct-write patterns at all.
var pkgManagerPinPatterns = []struct {
	re     *regexp.Regexp
	scheme string
}{
	{regexp.MustCompile(`\bgo\s+get\s+` + clause + `*?(?P<name>[\w.\-/]+)@(?P<version>v\d[\w.\-+]*)`), "golang"},
	{regexp.MustCompile(`\b(?:npm|pnpm|yarn)\s+(?:install|add|i)\b` + clause + `*?(?P<name>@[\w.\-]+/[\w.\-]+|[\w.\-]+)@(?P<version>\d[\w.\-+]*)`), "npm"},
	{regexp.MustCompile(`\bcargo\s+add\b` + clause + `*?(?P<name>[\w.\-]+)@(?P<version>\d[\w.\-+]*)`), "cargo"},
	{regexp.MustCompile(`\b(?:pip3?|poetry|uv)\s+(?:install|add)\b` + clause + `*?(?P<name>[\w.\-]+)==(?P<version>\d[\w.\-+]*)`), "pypi"},
}

// parsePkgManagerPin extracts the ecosystem, package name, and pinned
// version from a package manager CLI command, if cmd matches one of
// pkgManagerPinPatterns.
func parsePkgManagerPin(cmd string) (scheme, name, version string, ok bool) {
	for _, p := range pkgManagerPinPatterns {
		m := p.re.FindStringSubmatch(cmd)
		if m == nil {
			continue
		}
		for i, group := range p.re.SubexpNames() {
			switch group {
			case "name":
				name = m[i]
			case "version":
				version = m[i]
			}
		}
		return p.scheme, name, version, true
	}
	return "", "", "", false
}

// checkPkgManagerPin resolves name's latest released version under scheme
// and, if pinnedVersion is older, blocks (exit 2) with the same "outdated
// dependencies" message the Write/Edit path prints - so Claude retries with
// the correct version instead of pinning it via bash and never finding out.
// It exits 0 (fails open) if the purl can't be built or the resolver can't
// find a latest version, same as the Write/Edit path's own resolver errors.
func checkPkgManagerPin(scheme, name, pinnedVersion string) {
	res, err := resolver.NewEnrichmentResolver()
	if err != nil {
		return // fail open: a resolver construction error shouldn't block the command
	}

	// The resolver's response keys purls without a version component (see
	// pins.Diff / EnrichmentResolver.LatestVersions), same as every other
	// checker's manifest-parsed PURLs - so this must match, not carry
	// pinnedVersion.
	purlStr := purl.BuildPURLString(scheme, name, "", "")
	if purlStr == "" {
		return
	}

	pin := pins.Pin{Name: name, Version: pinnedVersion, PURL: purlStr}
	mismatches, err := pins.Diff(context.Background(), nil, map[string]pins.Pin{name: pin}, scheme, res, pins.NoRangeSupport, nil)
	if err != nil || len(mismatches) == 0 {
		return // fail open on a resolver error; nothing to flag if it's already latest
	}

	fmt.Fprintln(os.Stderr, "outdated dependency pinned via package manager CLI, use this version instead:")
	for _, m := range mismatches {
		fmt.Fprintf(os.Stderr, "  %s  %s -> %s\n", m.Name, m.Current, m.Latest)
	}
	os.Exit(2)
}

// runHook is a PreToolUse hook for the Write, Edit, and Bash tools.
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

	if in.ToolName == "Bash" {
		if looksLikeManifestWrite(in.ToolInput.Command) {
			fmt.Fprintln(os.Stderr, "yul: use the Write or Edit tool to modify dependency manifests, not bash (bash writes bypass the outdated-dependency check)")
			os.Exit(2)
		}
		if scheme, name, pinnedVersion, ok := parsePkgManagerPin(in.ToolInput.Command); ok {
			checkPkgManagerPin(scheme, name, pinnedVersion)
		}
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

	hasLockfile := manifestchecker.HasLockfile(filepath.Dir(in.ToolInput.FilePath), checker)

	mismatches, err := checker.Check(before, after, hasLockfile)
	if err != nil {
		fmt.Fprintf(os.Stderr, "hook: %v\n", err)
		os.Exit(0) // fail open: a resolver/network error shouldn't block the write
	}

	if len(mismatches) == 0 {
		os.Exit(0)
	}

	var outdated, ranges []mismatch.Mismatch
	for _, m := range mismatches {
		if m.Range {
			ranges = append(ranges, m)
		} else {
			outdated = append(outdated, m)
		}
	}

	if len(outdated) > 0 {
		fmt.Fprintln(os.Stderr, "outdated dependencies, use these versions instead:")
		for _, m := range outdated {
			name := m.Name
			if m.Namespace != "" {
				name = m.Namespace + ":" + m.Name
			}
			latest := m.Latest
			if m.Suggested != "" {
				latest = m.Suggested
			}
			fmt.Fprintf(os.Stderr, "  %s  %s -> %s\n", name, m.Current, latest)
		}
	}
	if len(ranges) > 0 {
		fmt.Fprintln(os.Stderr, "these pinned ranges need attention:")
		for _, m := range ranges {
			name := m.Name
			if m.Namespace != "" {
				name = m.Namespace + ":" + m.Name
			}
			if m.Suggested != "" {
				fmt.Fprintf(os.Stderr, "  %s  %s does not allow latest %s -> widen to %s\n", name, m.Current, m.Latest, m.Suggested)
			}
			if m.NoLockfile {
				fmt.Fprintf(os.Stderr, "  %s: no lockfile found next to this manifest -> run your package manager's install to generate one\n", name)
			}
		}
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
	cached, hadCache := scan.LoadCache(cachePath)
	if hadCache && cached.Fresh(version, scanCacheTTL, now, hash) {
		emitScanContext(scan.Unnotified(cached.Findings, cached.Notified), cached.ScannedAt)
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

	// Diff against what the *previous* cache already surfaced (even though
	// it's now stale) before overwriting it, so re-mentioning something
	// unrelated changing in the manifest doesn't also re-nag about a
	// finding the user already saw and chose to ignore.
	toNotify := scan.Unnotified(findings, cached.Notified)

	// Cache the result even if it's empty, so a clean project doesn't get
	// re-resolved every session either. Notified is set to the full
	// findings list, not just toNotify: everything computed this scan
	// counts as "surfaced" now, whether or not the user acts on it.
	_ = scan.SaveCache(cachePath, scan.Cache{
		YulVersion:    version,
		ManifestsHash: hash,
		ScannedAt:     now,
		ProjectDir:    dir,
		Findings:      findings,
		Notified:      findings,
	})

	emitScanContext(toNotify, now)
}

// emitScanContext prints the SessionStart hook JSON that adds findings to
// Claude's context, or nothing if there's nothing to report.
func emitScanContext(findings []scan.Finding, scannedAt time.Time) {
	if len(findings) == 0 {
		os.Exit(0)
	}

	var outdated, ranges []scan.Finding
	for _, f := range findings {
		if f.Range {
			ranges = append(ranges, f)
		} else {
			outdated = append(outdated, f)
		}
	}

	var b strings.Builder
	b.WriteString("yul scanned this project's manifests")
	fmt.Fprintf(&b, " (as of %s)", scannedAt.Format("2006-01-02"))
	b.WriteString(" and found:\n")
	if len(outdated) > 0 {
		fmt.Fprintf(&b, "%d pinned dependencies older than the latest release:\n", len(outdated))
		for _, f := range outdated {
			name := f.Name
			if f.Namespace != "" {
				name = f.Namespace + ":" + f.Name
			}
			latest := f.Latest
			if f.Suggested != "" {
				latest = f.Suggested
			}
			fmt.Fprintf(&b, "  %s: %s  %s -> %s\n", f.File, name, f.Current, latest)
		}
	}
	if len(ranges) > 0 {
		fmt.Fprintf(&b, "%d pinned ranges that need attention:\n", len(ranges))
		for _, f := range ranges {
			name := f.Name
			if f.Namespace != "" {
				name = f.Namespace + ":" + f.Name
			}
			if f.Suggested != "" {
				fmt.Fprintf(&b, "  %s: %s  %s does not allow latest %s -> widen to %s\n", f.File, name, f.Current, f.Latest, f.Suggested)
			}
			if f.NoLockfile {
				fmt.Fprintf(&b, "  %s: %s: no lockfile found next to this manifest\n", f.File, name)
			}
		}
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

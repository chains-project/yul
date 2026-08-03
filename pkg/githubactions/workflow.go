// Package githubactions checks GitHub Actions workflow files
// (.github/workflows/*.yml) for `uses:` references pinned older than
// what's actually released, using git-pkgs/manifests to parse the
// workflow and an injected resolver.Resolver to look up latest releases.
//
// Design notes (see chains-project/yul#4):
//
// Dispatch: every other ecosystem's checker owns a fixed manifest
// basename ("pom.xml", "package.json", ...), which is what
// manifestchecker.ManifestChecker.Filename() and the hook's
// filepath.Base() dispatch assume. Workflow files have arbitrary
// basenames (ci.yml, release.yml, ...) and are only identifiable by
// directory, so Checker instead implements manifestchecker.PathMatcher
// and is matched against the full path the hook was given.
//
// Tag vs. SHA pins: `uses:` refs are usually a mutable tag (@v4) or an
// immutable full commit SHA (the security-recommended pin). There's no
// git-pkgs/vers scheme for GitHub Actions, and even if there were,
// "outdated" doesn't reduce to a semver comparison the way it does for
// the other ecosystems - a commit SHA isn't a version at all. So this
// checker doesn't reuse pins.ExactVersion/pins.Diff: it treats a ref as
// comparable only when vers.Valid reports it looks like a version
// (rejecting branch names and commit SHAs alike, since neither parses as
// one), and falls back to vers.Compare's scheme-agnostic comparison
// rather than inventing a "githubactions" vers scheme. SHA-pinned and
// branch-pinned actions are left alone rather than flagged: verifying a
// SHA is stale would require resolving it to a release, which is out of
// scope here.
//
// Resolution coverage: whether git-pkgs/enrichment's ecosyste.ms-backed
// resolver actually has LatestVersion data for pkg:githubactions purls
// wasn't verified against the live API when this was written (network
// access to packages.ecosyste.ms wasn't available in that environment).
// If it doesn't, every changed action reference simply fails to resolve,
// which - per pins.Diff's existing "no latest version found" behavior
// mirrored below - the hook already treats as fail-open (an unresolvable
// purl is a resolver error, not a mismatch), so this degrades safely to
// "never blocks" rather than blocking incorrectly.
package githubactions

import (
	"context"
	"fmt"
	"strings"

	"github.com/git-pkgs/manifests"
	"github.com/git-pkgs/vers"

	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/chains-project/yul/pkg/util/resolver"
)

// workflowFilename is passed to manifests.Parse to select its
// github-actions parser. The parser identifies workflows by directory
// (.github/workflows/) rather than by content, and also accepts this
// exact basename as a fallback for standalone testing, so its choice
// here doesn't affect parsing - only Checker.MatchesPath decides which
// real files get routed to this checker.
const workflowFilename = ".github/workflows/workflow.yml"

// Checker implements manifestchecker.ManifestChecker (and
// manifestchecker.PathMatcher) for GitHub Actions workflow files.
type Checker struct {
	// Resolver resolves latest released versions. main.go wires up an
	// enrichment-backed resolver; tests inject a fake one.
	Resolver resolver.Resolver
}

// Filename is documentation-only here: workflow files don't share a
// fixed basename, so dispatch actually goes through MatchesPath.
func (Checker) Filename() string { return ".github/workflows/*.yml" }

// MatchesPath reports whether path is a GitHub Actions workflow file,
// deferring to git-pkgs/manifests' own notion of what counts as one
// (a .yml/.yaml file inside a .github/workflows directory).
func (Checker) MatchesPath(path string) bool {
	eco, kind, ok := manifests.Identify(path)
	return ok && eco == "github-actions" && kind == manifests.Manifest
}

func (c Checker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckWorkflow(before, after, c.Resolver)
}

// actionPin is a GitHub Action reference pinned to a version-like tag
// (never a branch name or commit SHA - see the package doc comment),
// along with the PURL to resolve its latest version through.
type actionPin struct {
	name    string // e.g. "actions/checkout", or "actions/cache/restore" for a subpath action
	version string // the ref as written, e.g. "v4" - never rewritten or v-stripped
	purl    string
}

// parseWorkflowPins parses a workflow file's content and returns its
// GitHub Action steps (`uses: owner/repo@ref`) that are pinned to
// something that looks like a version. Docker container/service image
// references and local actions (`uses: ./...`) are never produced by
// git-pkgs/manifests' own dependency extraction for this purpose and are
// skipped; branch names and commit SHAs don't parse as a version and are
// skipped too, since there's nothing to compare them against.
func parseWorkflowPins(content string) (map[string]actionPin, error) {
	result := make(map[string]actionPin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse(workflowFilename, []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing workflow: %w", err)
	}

	for _, dep := range parsed.Dependencies {
		if strings.HasPrefix(dep.Name, "docker://") {
			continue // container image pins are a different ecosystem
		}
		if dep.Version == "" || !vers.Valid(dep.Version) {
			continue
		}
		result[dep.Name] = actionPin{name: dep.Name, version: dep.Version, purl: dep.PURL}
	}
	return result, nil
}

// CheckWorkflow compares workflow content before and after a Write and
// reports any version-pinned action reference that is newly added or
// whose pinned ref was just changed, and doesn't match the latest
// release res knows about. References the write didn't touch, or that
// aren't pinned to something version-shaped, are left alone.
func CheckWorkflow(before, after string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	beforePins, err := parseWorkflowPins(before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parseWorkflowPins(after)
	if err != nil {
		return nil, err
	}

	var changed []actionPin
	for name, pin := range afterPins {
		if prior, ok := beforePins[name]; ok && prior.version == pin.version {
			continue // untouched by this write
		}
		changed = append(changed, pin)
	}
	if len(changed) == 0 {
		return nil, nil
	}

	purls := make([]string, len(changed))
	for i, pin := range changed {
		purls[i] = pin.purl
	}

	latest, err := res.LatestVersions(context.Background(), purls)
	if err != nil {
		return nil, fmt.Errorf("resolving latest versions: %w", err)
	}

	var mismatches []mismatch.Mismatch
	for _, pin := range changed {
		latestVersion, ok := latest[pin.purl]
		if !ok {
			return nil, fmt.Errorf("resolving %s: no latest version found", pin.name)
		}
		if vers.Compare(pin.version, latestVersion) != 0 {
			mismatches = append(mismatches, mismatch.Mismatch{
				Name:    pin.name,
				Current: pin.version,
				Latest:  latestVersion,
			})
		}
	}
	return mismatches, nil
}

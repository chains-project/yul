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
// immutable full commit SHA (the security-recommended pin, and the one
// GitHub's own hardening guidance and tools like StepSecurity's
// pin-github-actions push toward). There's no git-pkgs/vers scheme for
// GitHub Actions, and even if there were, "outdated" doesn't reduce to a
// semver comparison the way it does for the other ecosystems - a commit
// SHA isn't a version at all. So this checker doesn't reuse
// pins.ExactVersion/pins.Diff: it treats a ref as comparable when it
// matches vers.SemanticVersionRegex (an optional "v" then a leading
// digit), which a branch name never does and a bare SHA never does
// either. This is deliberately stricter than vers.Valid: that helper's
// generic fallback parser treats almost any hyphenated string as a
// "version" with an ignored non-numeric major (e.g. "not-a-version"
// parses "successfully" as major 0), which would make free-text comments
// and branch names like "release-4.0" look version-shaped when they
// aren't.
//
// A SHA pin conventionally carries its human-readable version alongside
// it as a trailing YAML comment, e.g.
// `uses: actions/checkout@<40-hex-sha> # v4.2.1`, specifically so tools
// (and reviewers) can tell what release the pin corresponds to without
// resolving the commit. Since that comment isn't part of
// git-pkgs/manifests' parsed dependency data, shaCommentPin does a second,
// regex-based pass over the raw content to recover it, and that recovered
// tag - not the SHA - is what gets compared and reported. This trusts the
// comment to accurately describe the pinned commit, same as Dependabot
// does; this checker has no independent way to confirm a SHA and its
// comment actually match, or that the tag it names is itself an immutable
// ref. A SHA with no such comment, or a branch pin, is left alone: there's
// nothing to compare it against.
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
	"regexp"
	"strings"

	"github.com/git-pkgs/manifests"
	"github.com/git-pkgs/vers"

	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/chains-project/yul/pkg/util/resolver"
)

// shaCommentPin matches a `uses: owner/repo@<40-hex-sha> # <tag>` line -
// see the package doc comment - capturing the action name and the tag
// named in the comment.
var shaCommentPin = regexp.MustCompile(`uses:\s*([^\s@]+)@([0-9a-fA-F]{40})\s*#\s*(\S+)`)

// looksLikeVersion reports whether s is shaped like a version tag - an
// optional "v"/"V" followed by a leading digit - rather than a branch
// name, a free-text comment, or anything else with no comparable
// version. See the package doc comment for why this is stricter than
// vers.Valid.
func looksLikeVersion(s string) bool {
	return vers.SemanticVersionRegex.MatchString(s)
}

// parseShaComments scans content for the SHA-pin-with-version-comment
// convention and returns the version named for each action and SHA pair,
// but only when that comment text itself looks like a version. Keying by
// both values keeps repeated uses of the same action distinct.
func parseShaComments(content string) map[string]string {
	result := make(map[string]string)
	for _, m := range shaCommentPin.FindAllStringSubmatch(content, -1) {
		name, sha, tag := m[1], strings.ToLower(m[2]), m[3]
		if looksLikeVersion(tag) {
			result[name+"@"+sha] = tag
		}
	}
	return result
}

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

	// Sha resolves a release tag's commit SHA, so mismatches can suggest
	// the `@<sha> # <tag>` pin convention (see CheckWorkflow). Optional:
	// a nil Sha just leaves Mismatch.Suggested unset, falling back to the
	// bare tag - the same fail-open treatment given to any other
	// resolver error here.
	Sha ShaResolver
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
	return CheckWorkflow(before, after, c.Resolver, c.Sha)
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
// something comparable: a ref that's version-shaped on its own (a tag),
// or a commit SHA carrying the version-comment convention (see the
// package doc comment and parseShaComments). Docker container/service
// image references and local actions (`uses: ./...`) are never produced
// by git-pkgs/manifests' own declarations for this purpose and
// are skipped; branch names and bare (uncommented) commit SHAs skip too,
// since there's nothing to compare them against.
func parseWorkflowPins(content string) (map[string]actionPin, error) {
	result := make(map[string]actionPin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse(workflowFilename, []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing workflow: %w", err)
	}
	shaComments := parseShaComments(content)

	for _, declaration := range parsed.Declarations {
		if declaration.Version == "" {
			continue
		}

		version := declaration.Version
		if !looksLikeVersion(version) {
			tag, ok := shaComments[declaration.Name+"@"+strings.ToLower(version)]
			if !ok {
				continue
			}
			version = tag
		}
		result[declaration.Location] = actionPin{
			name:    declaration.Name,
			version: version,
			purl:    declaration.PURL,
		}
	}
	return result, nil
}

// CheckWorkflow compares workflow content before and after a Write and
// reports any version-pinned action reference that is newly added or
// whose pinned ref was just changed, and is older than the latest
// release res knows about. References the write didn't touch, or that
// aren't pinned to something version-shaped, are left alone.
func CheckWorkflow(before, after string, res resolver.Resolver, shaRes ShaResolver) ([]mismatch.Mismatch, error) {
	beforePins, err := parseWorkflowPins(before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parseWorkflowPins(after)
	if err != nil {
		return nil, err
	}

	var changed []actionPin
	for location, pin := range afterPins {
		if prior, ok := beforePins[location]; ok && prior == pin {
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
		if vers.Compare(pin.version, latestVersion) < 0 {
			mismatches = append(mismatches, mismatch.Mismatch{
				Name:    pin.name,
				Current: pin.version,
				Latest:  latestVersion,
			})
		}
	}

	if shaRes != nil {
		for i := range mismatches {
			sha, err := shaRes.ResolveSHA(context.Background(), repoOf(mismatches[i].Name), mismatches[i].Latest)
			if err != nil {
				continue // fail open: report the plain tag instead
			}
			mismatches[i].Suggested = fmt.Sprintf("%s # %s", sha, mismatches[i].Latest)
		}
	}

	return mismatches, nil
}

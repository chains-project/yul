// Package golang checks go.mod for required modules pinned older than
// what's actually released, using git-pkgs/manifests to parse the module
// file and an injected resolver.Resolver to look up latest releases.
//
// Design notes (see chains-project/yul#4):
//
// What counts as an "exact pin": unlike pom.xml/package.json/requirements.txt,
// go.mod's `require` syntax has no range/wildcard/dist-tag operators at all -
// every entry is already a single module@version pair, so there's no
// bare-vs-operator disambiguation to do (pins.ExactVersion is still called,
// with requireOperator=false, purely to reject anything malformed rather
// than to filter out looser specifiers, since none exist here).
//
// Pseudo-versions: a module pinned to an untagged commit uses Go's
// pseudo-version format (e.g. "v0.0.0-20210101000000-abcdef123456"), which
// git-pkgs/vers' "golang" scheme compares as a semver prerelease - always
// older than any real tagged release, per semver precedence rules. That
// means a deliberately-pinned pseudo-version (a legitimate way to pick up
// an unreleased fix before the next tag) always reports as outdated against
// the latest tag. This checker doesn't special-case that: it's a rare
// enough thing for Claude to write unprompted, and treating it as
// "outdated" is directionally correct even if the pin was deliberate - the
// hook block just tells Claude what the latest tagged release actually is.
//
// Build metadata: a "+incompatible" suffix (used by v2+ modules that
// predate module-aware tagging) is build metadata under semver precedence,
// so git-pkgs/vers ignores it when comparing - "v2.3.4+incompatible" and
// "v2.3.4" compare equal.
//
// Minimum version selection: the version in a require line is a *minimum*
// - Go's MVS may resolve the actual build to something higher because
// another module in the graph requires more. This checker, like every
// other ecosystem checker here, only ever looks at the manifest's own
// literal declaration, never a resolved/effective graph, so this isn't a
// special case; it's called out here because MVS is what could make
// "declared version" sound like a strange thing to check for go.mod
// specifically, when it's really the same posture as everywhere else.
//
// Parser coverage: git-pkgs/manifests' go.mod parser only extracts
// `require` entries (single-line and block form); it does not surface
// `replace` directives as dependencies. A stale version introduced via
// `replace module => module vX.Y.Z` therefore isn't visible to this
// checker - the same category of blind spot as e.g. Maven's <parent>
// version being a property reference.
//
// Resolution coverage: whether git-pkgs/enrichment's ecosyste.ms-backed
// resolver has LatestVersion data for pkg:golang purls wasn't verified
// against the live API when this was written (network access to
// packages.ecosyste.ms wasn't available in that environment, same gap
// noted in pkg/githubactions). An unresolvable purl is treated as a
// resolver error rather than a mismatch, so this degrades safely to
// "never blocks" rather than blocking incorrectly.
package golang

import (
	"context"
	"fmt"
	"strings"

	"github.com/git-pkgs/manifests"

	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/chains-project/yul/pkg/util/pins"
	"github.com/chains-project/yul/pkg/util/resolver"
)

const scheme = "golang"

// Checker implements manifestchecker.ManifestChecker for go.mod.
type Checker struct {
	// Resolver resolves latest released versions. main.go wires up an
	// enrichment-backed resolver; tests inject a fake one.
	Resolver resolver.Resolver
}

func (Checker) Filename() string { return "go.mod" }

func (c Checker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckGoMod(before, after, c.Resolver)
}

// parseGoModPins parses go.mod content and returns its required modules,
// keyed by module path. Every require entry - single-line or block form,
// direct or "// indirect" - is a bare module@version pair with no operator,
// so pins.ExactVersion's role here is only to reject anything malformed.
func parseGoModPins(content string) (map[string]pins.Pin, error) {
	result := make(map[string]pins.Pin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse("go.mod", []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing go.mod: %w", err)
	}

	for _, dep := range parsed.Dependencies {
		version, ok := pins.ExactVersion(dep.Version, scheme, false)
		if !ok {
			continue
		}
		result[dep.Name] = pins.Pin{Name: dep.Name, Version: version, PURL: dep.PURL}
	}
	return result, nil
}

// CheckGoMod compares go.mod content before and after a Write and reports
// any required module that is newly added or whose pinned version was just
// changed, and doesn't match the latest release res knows about. Modules
// the write didn't touch are left alone, even if outdated.
func CheckGoMod(before, after string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	beforePins, err := parseGoModPins(before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parseGoModPins(after)
	if err != nil {
		return nil, err
	}
	return pins.Diff(context.Background(), beforePins, afterPins, scheme, res)
}

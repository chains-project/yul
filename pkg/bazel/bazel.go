// Package bazel checks MODULE.bazel for bazel_dep entries pinned older than
// what's actually released, using git-pkgs/manifests to parse the module
// file and an injected resolver.Resolver to look up latest releases.
//
// Design notes (see chains-project/yul#4):
//
// Why this ecosystem matters more than most: there's no `bazel add`-style
// command that resolves a module's latest Bazel Central Registry release
// and writes it into MODULE.bazel; a `bazel_dep(name = ..., version =
// ...)` entry is always hand-typed, so nothing steers Claude away from a
// version recalled from training data the way `cargo add`/`go get` do for
// their ecosystems.
//
// What counts as an "exact pin": bzlmod's dependency format has no range
// syntax at all (no `^`/`~`/`>=`) - every `bazel_dep` version is already a
// bare literal, same situation as go.mod's `require` entries.
// pins.ExactVersion is still called, with requireOperator=false, purely to
// reject anything malformed (e.g. an empty version string). git-pkgs/vers
// has no dedicated "bazel" scheme, so both the exactness check and the
// final comparison fall back to its generic version parser/comparator -
// adequate for the dotted numeric versions the Bazel Central Registry
// uses.
//
// Scope: only MODULE.bazel (bzlmod) is covered, matching
// git-pkgs/manifests' own coverage - legacy WORKSPACE-based
// http_archive/git_repository rules aren't a dependency format it parses,
// so they're out of scope until upstream adds that parser.
//
// git-pkgs/manifests' bazel parser doesn't populate ParseResult.Declarations,
// so pins are keyed by module name alone, same as go.mod's require entries;
// a module isn't expected to appear more than once in a single
// MODULE.bazel.
//
// Resolution coverage: whether git-pkgs/enrichment resolves pkg:bazel
// purls wasn't verified against the live API in this environment (same
// gap noted in pkg/golang and pkg/githubactions); an unresolvable purl
// simply fails open per pins.Diff.
package bazel

import (
	"context"
	"fmt"
	"strings"

	"github.com/git-pkgs/manifests"

	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/chains-project/yul/pkg/util/pins"
	"github.com/chains-project/yul/pkg/util/resolver"
)

const scheme = "bazel"

// Checker implements manifestchecker.ManifestChecker for MODULE.bazel.
type Checker struct {
	// Resolver resolves latest released versions. main.go wires up an
	// enrichment-backed resolver; tests inject a fake one.
	Resolver resolver.Resolver
}

func (Checker) Filename() string { return "MODULE.bazel" }

func (c Checker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckModuleBazel(before, after, c.Resolver)
}

// parseModuleBazelPins parses MODULE.bazel content and returns its
// bazel_dep entries, keyed by module name. Every entry - direct or
// dev_dependency - is a bare name@version pair with no operator, so
// pins.ExactVersion's role here is only to reject anything malformed.
func parseModuleBazelPins(content string) (map[string]pins.Pin, error) {
	result := make(map[string]pins.Pin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse("MODULE.bazel", []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing MODULE.bazel: %w", err)
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

// CheckModuleBazel compares MODULE.bazel content before and after a Write
// and reports any bazel_dep entry that is newly added or whose pinned
// version was just changed, and doesn't match the latest release res knows
// about. Entries the write didn't touch are left alone, even if outdated.
func CheckModuleBazel(before, after string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	beforePins, err := parseModuleBazelPins(before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parseModuleBazelPins(after)
	if err != nil {
		return nil, err
	}
	return pins.Diff(context.Background(), beforePins, afterPins, scheme, res)
}

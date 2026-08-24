// Package cocoapods checks Podfile for pods pinned to an exact version
// older than what's actually released, using git-pkgs/manifests to parse
// the manifest and an injected resolver.Resolver to look up latest
// releases.
//
// Design notes (see chains-project/yul#4):
//
// Why this ecosystem matters more than most: CocoaPods has no `pod add`
// equivalent - `pod install`/`pod update` only resolve versions for pods
// already listed in the Podfile, they never add a new `pod` line to it.
// Adding a dependency means hand-typing a `pod "Name", "x.y.z"` line, so
// there's no CLI path that keeps Claude from typing a stale version the
// way `cargo add`/`go get`/`npm install` do for their ecosystems.
//
// What counts as an "exact pin": CocoaPods reuses RubyGems' version
// requirement operators (`=`, `!=`, `>`, `<`, `>=`, `<=`, `~>`), and - like
// RubyGems - a bare version literal with no operator (`pod "Alamofire",
// "5.6.4"`) means exact equality, not a floor. requireOperator=false
// mirrors npm/go's Checkers rather than Cargo/Poetry's. git-pkgs/vers has
// no dedicated "cocoapods" scheme, so pins.ExactVersion falls back to its
// generic constraint/version parser, which only recognizes single/double
// -character operators (`=`, `!=`, `<`, `>`, `<=`, `>=`) - it doesn't know
// `~>` as an operator at all, and its generic version validator is lenient
// enough to accept "~> 1.0" as a literal "exact" version instead of
// rejecting it. isPessimisticConstraint filters that case out before it
// ever reaches pins.ExactVersion.
//
// git-pkgs/manifests' Podfile parser doesn't populate
// ParseResult.Declarations, so pins are keyed by scope+name instead of a
// declaration location, same as pkg/cargo. Its target-tracking is a
// coarse Runtime/Test split keyed on whether the enclosing `target ...
// do` block's name contains "test" - two non-test targets pinning the
// same pod to different versions collapse into one "runtime" key, a
// parser-level blind spot this checker inherits rather than works around.
//
// Resolution coverage: whether git-pkgs/enrichment resolves pkg:cocoapods
// purls wasn't verified against the live API in this environment (same
// gap noted in pkg/golang and pkg/githubactions); an unresolvable purl
// simply fails open per pins.Diff.
package cocoapods

import (
	"context"
	"fmt"
	"strings"

	"github.com/git-pkgs/manifests"

	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/chains-project/yul/pkg/util/pins"
	"github.com/chains-project/yul/pkg/util/resolver"
)

const scheme = "cocoapods"

// Checker implements manifestchecker.ManifestChecker for Podfile.
type Checker struct {
	// Resolver resolves latest released versions. main.go wires up an
	// enrichment-backed resolver; tests inject a fake one.
	Resolver resolver.Resolver
}

func (Checker) Filename() string { return "Podfile" }

func (c Checker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckPodfile(before, after, c.Resolver)
}

// parsePodfilePins parses Podfile content and returns its exactly-pinned
// pods, keyed by "<scope>/<name>" since the parser doesn't expose a stable
// per-declaration location the way npm/pypi's do.
func parsePodfilePins(content string) (map[string]pins.Pin, error) {
	result := make(map[string]pins.Pin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse("Podfile", []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing Podfile: %w", err)
	}

	for _, dep := range parsed.Dependencies {
		// A pod with no version ("pod \"Name\"") means "any version" -
		// nothing exact to compare.
		if isPessimisticConstraint(dep.Version) {
			continue
		}
		version, ok := pins.ExactVersion(dep.Version, scheme, false)
		if !ok {
			continue
		}
		location := string(dep.Scope) + "/" + dep.Name
		result[location] = pins.Pin{Name: dep.Name, Version: version, PURL: dep.PURL}
	}
	return result, nil
}

// isPessimisticConstraint reports whether spec uses CocoaPods'/RubyGems'
// `~>` pessimistic operator (e.g. "~> 1.0"), the one requirement operator
// git-pkgs/vers' generic constraint parser (used here because there's no
// dedicated "cocoapods" scheme) doesn't recognize - see the package doc
// comment for why this must be filtered out before pins.ExactVersion.
func isPessimisticConstraint(spec string) bool {
	return strings.HasPrefix(strings.TrimSpace(spec), "~>")
}

// CheckPodfile compares Podfile content before and after a Write and
// reports any exactly-pinned pod that is newly added or whose pinned
// version was just changed, and is older than the latest release res
// knows about. Pods the write didn't touch, or that aren't pinned exactly
// (unversioned, or a `~>`/comparison-operator constraint), are left alone.
func CheckPodfile(before, after string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	beforePins, err := parsePodfilePins(before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parsePodfilePins(after)
	if err != nil {
		return nil, err
	}
	return pins.Diff(context.Background(), beforePins, afterPins, scheme, res)
}

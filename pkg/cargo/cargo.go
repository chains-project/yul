// Package cargo checks Cargo.toml for dependencies whose version
// requirement is based on an older version than what's actually released,
// using git-pkgs/manifests to parse the manifest and an injected
// resolver.Resolver to look up latest releases.
//
// Design notes (see chains-project/yul#4 and #43):
//
// Cargo's default requirement operator is caret, so a bare version like
// `serde = "1.2.3"` means `^1.2.3`, not an exact pin. That's still a
// requirement with one base version, so it's bumped in place: a stale
// `"1.2.3"` is reported as `"1.5.0"` (still a caret range), `=1.2.3` as
// `=1.5.0`, and so on. bareIsRange=true in pins.ParseSpec accepts the bare
// form, matching pyproject.toml's Poetry tables.
//
// git-pkgs/manifests' Cargo.toml parser doesn't populate
// ParseResult.Declarations like npm/pypi/maven/github_actions do, so pins
// are keyed by scope+name instead of a declaration location.
//
// Resolution coverage: whether git-pkgs/enrichment resolves pkg:cargo purls
// wasn't verified against the live API in this environment (same gap noted
// in pkg/golang and pkg/githubactions); an unresolvable purl simply fails
// open per pins.Diff.
package cargo

import (
	"context"
	"fmt"
	"strings"

	"github.com/git-pkgs/manifests"

	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/chains-project/yul/pkg/util/pins"
	"github.com/chains-project/yul/pkg/util/resolver"
)

const scheme = "cargo"

// Checker implements manifestchecker.ManifestChecker for Cargo.toml.
type Checker struct {
	// Resolver resolves latest released versions. main.go wires up an
	// enrichment-backed resolver; tests inject a fake one.
	Resolver resolver.Resolver
}

func (Checker) Filename() string { return "Cargo.toml" }

func (c Checker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckCargoToml(before, after, c.Resolver)
}

// parseCargoPins parses Cargo.toml content and returns every dependency
// across [dependencies], [dev-dependencies], and [build-dependencies] whose
// requirement has a single base version to keep current (bare/caret, "^",
// "~", "=", ">="), keyed by "<scope>/<name>" since the parser doesn't expose
// a stable per-declaration location the way npm/pypi's do. Wildcards ("*",
// "1.*") and multi-clause ranges are left alone.
func parseCargoPins(content string) (map[string]pins.Pin, error) {
	result := make(map[string]pins.Pin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse("Cargo.toml", []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing Cargo.toml: %w", err)
	}

	for _, dep := range parsed.Dependencies {
		// Local path deps (`{ path = "../local" }`) are already dropped by
		// the parser; workspace-inherited deps come through as "*", which
		// ParseSpec rejects below.
		spec, ok := pins.ParseSpec(dep.Version, scheme, true)
		if !ok {
			continue
		}
		location := string(dep.Scope) + "/" + dep.Name
		result[location] = pins.Pin{Name: dep.Name, Operator: spec.Operator, Version: spec.Version, PURL: dep.PURL}
	}
	return result, nil
}

// CheckCargoToml compares Cargo.toml content before and after a Write and
// reports any crate that is newly added or whose requirement was just
// changed, and whose base version is older than the latest release res
// knows about. The suggested replacement keeps the requirement's operator.
// Crates the write didn't touch, or whose requirement has no single base
// version, are left alone.
func CheckCargoToml(before, after string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	beforePins, err := parseCargoPins(before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parseCargoPins(after)
	if err != nil {
		return nil, err
	}
	return pins.Diff(context.Background(), beforePins, afterPins, scheme, res)
}

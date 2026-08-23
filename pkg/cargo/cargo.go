// Package cargo checks Cargo.toml for dependencies pinned older than what's
// actually released, using git-pkgs/manifests to parse the manifest and an
// injected resolver.Resolver to look up latest releases.
//
// Design notes (see chains-project/yul#4):
//
// What counts as an "exact pin": Cargo's default requirement operator is
// caret, so a bare version like `serde = "1.2.3"` means `^1.2.3`, not an
// exact pin - only an explicit `=1.2.3` is exact. requireOperator=true is
// passed to pins.ExactVersion for this, matching pyproject.toml's Poetry
// tables (same "bare version is a range" gotcha). In practice
// git-pkgs/vers' "cargo" scheme already parses a bare version natively as a
// caret range, so ExactVersion would reject it even with
// requireOperator=false; the flag is kept anyway for defense-in-depth and to
// document the intent explicitly, same as pyproject.go.
//
// Table-form dependencies (`regex = { version = "1.2.3" }`) go through the
// same ExactVersion check as string-form ones - git-pkgs/manifests already
// extracts the "version" key for both. Local path dependencies
// (`{ path = "../local" }`) are dropped by the parser entirely, and
// workspace-inherited dependencies (`{ workspace = true }`) come through
// with version "*", which ExactVersion rejects like any other non-exact
// spec.
//
// Parser coverage: unlike npm/pypi/maven/github_actions, git-pkgs/manifests'
// Cargo.toml parser doesn't populate ParseResult.Declarations, so there's no
// stable per-declaration Location to key pins by. This checker instead
// builds its own key from scope+name (dependencies/dev-dependencies/
// build-dependencies sections can each pin the same crate independently),
// the same Dependencies-based fallback pkg/golang uses for go.mod.
//
// Resolution coverage: whether git-pkgs/enrichment's ecosyste.ms-backed
// resolver actually has LatestVersion data for pkg:cargo purls wasn't
// verified against the live API when this was written (network access to
// packages.ecosyste.ms wasn't available in that environment, same gap noted
// in pkg/golang and pkg/githubactions). If it doesn't, every changed crate
// simply fails to resolve, which - per pins.Diff's existing "no latest
// version found" behavior - the hook already treats as fail-open, so this
// degrades safely to "never blocks" rather than blocking incorrectly.
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

// parseCargoPins parses Cargo.toml content and returns its exactly-pinned
// ("=") dependencies across [dependencies], [dev-dependencies], and
// [build-dependencies], keyed by "<scope>/<name>" since the parser doesn't
// expose a stable per-declaration location the way npm/pypi's do.
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
		version, ok := pins.ExactVersion(dep.Version, scheme, true)
		if !ok {
			continue
		}
		location := string(dep.Scope) + "/" + dep.Name
		result[location] = pins.Pin{Name: dep.Name, Version: version, PURL: dep.PURL}
	}
	return result, nil
}

// CheckCargoToml compares Cargo.toml content before and after a Write and
// reports any exactly-pinned ("=") crate that is newly added or whose
// pinned version was just changed, and is older than the latest release res
// knows about. Crates the write didn't touch, or that aren't pinned
// exactly, are left alone.
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

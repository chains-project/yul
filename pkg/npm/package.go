// Package npm checks package.json for dependencies pinned older than
// what's actually released, using git-pkgs/manifests to parse the manifest
// and an injected resolver.Resolver to look up latest releases.
package npm

import (
	"context"
	"fmt"
	"strings"

	"github.com/git-pkgs/manifests"

	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/chains-project/yul/pkg/util/pins"
	"github.com/chains-project/yul/pkg/util/resolver"
)

const scheme = "npm"

// Checker implements manifestchecker.ManifestChecker for package.json.
type Checker struct {
	// Resolver resolves latest released versions. main.go wires up an
	// enrichment-backed resolver; tests inject a fake one.
	Resolver resolver.Resolver
}

func (Checker) Filename() string { return "package.json" }

// LockfileNames lists the lockfiles the major npm-compatible package
// managers produce alongside package.json.
func (Checker) LockfileNames() []string {
	return []string{"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lock", "bun.lockb"}
}

func (c Checker) Check(before, after string, hasLockfile bool) ([]mismatch.Mismatch, error) {
	return CheckPackageJSON(before, after, c.Resolver, hasLockfile)
}

// parsePackageJSON parses package.json content and returns its exactly-pinned
// (no "^", "~", range, wildcard, tag, or protocol prefix) and range-pinned
// dependencies across dependencies, devDependencies, optionalDependencies,
// and peerDependencies.
func parsePackageJSON(content string) (map[string]pins.Pin, error) {
	result := make(map[string]pins.Pin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse("package.json", []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing package.json: %w", err)
	}

	for _, declaration := range parsed.Declarations {
		if version, ok := pins.ExactVersion(declaration.Version, scheme, false); ok {
			result[declaration.Location] = pins.Pin{
				Name: declaration.Name,
				Spec: version,
				PURL: declaration.PURL,
			}
		} else if pins.IsRange(declaration.Version, scheme, false) {
			result[declaration.Location] = pins.Pin{
				Name:  declaration.Name,
				Spec:  strings.TrimSpace(declaration.Version),
				PURL:  declaration.PURL,
				Range: true,
			}
		}
	}
	return result, nil
}

// formatRangeFix renders a caret range anchored at latest, replacing a
// range that excludes it.
func formatRangeFix(_, latest string) string { return "^" + latest }

// CheckPackageJSON compares package.json content before and after a Write
// and reports outdated exact pins, ranges that exclude the latest release
// (recommending a caret range anchored at it instead), and ranges with no
// lockfile alongside package.json. Packages the write didn't touch are
// left alone.
func CheckPackageJSON(before, after string, res resolver.Resolver, hasLockfile bool) ([]mismatch.Mismatch, error) {
	beforePins, err := parsePackageJSON(before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parsePackageJSON(after)
	if err != nil {
		return nil, err
	}
	return pins.Diff(context.Background(), beforePins, afterPins, scheme, res, hasLockfile, formatRangeFix)
}

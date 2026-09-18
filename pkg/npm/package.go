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

func (c Checker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckPackageJSON(before, after, c.Resolver)
}

// parsePackageJSON parses package.json content and returns its exactly-pinned
// dependencies (no "^", "~", range, wildcard, tag, or protocol prefix) and
// its range-pinned dependencies, across dependencies, devDependencies,
// optionalDependencies, and peerDependencies.
func parsePackageJSON(content string) (map[string]pins.Pin, map[string]pins.RangePin, error) {
	exact := make(map[string]pins.Pin)
	ranges := make(map[string]pins.RangePin)
	if strings.TrimSpace(content) == "" {
		return exact, ranges, nil
	}

	parsed, err := manifests.Parse("package.json", []byte(content))
	if err != nil {
		return nil, nil, fmt.Errorf("parsing package.json: %w", err)
	}

	for _, declaration := range parsed.Declarations {
		if version, ok := pins.ExactVersion(declaration.Version, scheme, false); ok {
			exact[declaration.Location] = pins.Pin{
				Name:    declaration.Name,
				Version: version,
				PURL:    declaration.PURL,
			}
		} else if pins.IsRange(declaration.Version, scheme, false) {
			ranges[declaration.Location] = pins.RangePin{
				Name: declaration.Name,
				Spec: strings.TrimSpace(declaration.Version),
				PURL: declaration.PURL,
			}
		}
	}
	return exact, ranges, nil
}

// formatExactPin renders a latest version as npm's exact-pin syntax.
func formatExactPin(latest string) string { return latest }

// CheckPackageJSON compares package.json content before and after a Write
// and reports outdated exact pins plus ranges that exclude the latest
// release, recommending a hard pin for each. Packages the write didn't
// touch are left alone.
func CheckPackageJSON(before, after string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	beforePins, beforeRanges, err := parsePackageJSON(before)
	if err != nil {
		return nil, err
	}
	afterPins, afterRanges, err := parsePackageJSON(after)
	if err != nil {
		return nil, err
	}
	mismatches, err := pins.Diff(context.Background(), beforePins, afterPins, scheme, res)
	if err != nil {
		return nil, err
	}

	rangeMismatches, err := pins.DiffRanges(context.Background(), beforeRanges, afterRanges, scheme, res, formatExactPin)
	if err != nil {
		return nil, err
	}

	return append(mismatches, rangeMismatches...), nil
}

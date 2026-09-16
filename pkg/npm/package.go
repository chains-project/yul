// Package npm checks package.json for dependencies whose version
// requirement is based on an older version than what's actually released, using git-pkgs/manifests to parse the manifest
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

// parsePackageJSONPins parses package.json content and returns every
// dependency across dependencies, devDependencies, optionalDependencies,
// and peerDependencies whose requirement has a single base version to keep
// current: an exact pin, or a "^", "~", or ">=" range. Compound ranges,
// x-ranges ("1.x"), wildcards, dist-tags, and protocol specs (workspace:,
// file:, git) are left alone.
func parsePackageJSONPins(content string) (map[string]pins.Pin, error) {
	result := make(map[string]pins.Pin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse("package.json", []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing package.json: %w", err)
	}

	for _, declaration := range parsed.Declarations {
		operator, version, ok := pins.ParseSpec(declaration.Version, scheme, false)
		if !ok {
			continue
		}
		result[declaration.Location] = pins.Pin{
			Name:     declaration.Name,
			Operator: operator,
			Version:  version,
			PURL:     declaration.PURL,
		}
	}
	return result, nil
}

// CheckPackageJSON compares package.json content before and after a Write
// and reports any package that is newly added or whose requirement was just
// changed, and whose base version is older than the latest release res
// knows about. The suggested replacement keeps the requirement's operator
// ("^1.0.0" -> "^2.0.0"). Packages the write didn't touch, or whose
// requirement has no single base version, are left alone.
func CheckPackageJSON(before, after string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	beforePins, err := parsePackageJSONPins(before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parsePackageJSONPins(after)
	if err != nil {
		return nil, err
	}
	return pins.Diff(context.Background(), beforePins, afterPins, scheme, res)
}

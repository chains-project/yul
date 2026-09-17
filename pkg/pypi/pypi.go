// Package pypi checks requirements.txt and pyproject.toml for dependencies
// pinned older than what's actually released, using git-pkgs/manifests to
// parse manifests and an injected resolver.Resolver to look up latest
// releases.
package pypi

import (
	"fmt"
	"strings"

	"github.com/git-pkgs/manifests"
	"github.com/git-pkgs/purl"

	"github.com/chains-project/yul/pkg/util/pins"
)

const scheme = "pypi"

// parsePypiPins parses filename's content (requirements.txt or
// pyproject.toml) and returns its exactly-pinned ("==") dependencies, keyed
// by their source declaration location and named by their canonical PURL
// package name.
func parsePypiPins(filename, content string) (map[string]pins.Pin, error) {
	result := make(map[string]pins.Pin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse(filename, []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing %s: %w", filename, err)
	}

	for _, declaration := range parsed.Declarations {
		version, ok := pins.ExactVersion(declaration.Version, scheme, true)
		if !ok {
			continue
		}
		canonical, err := purl.Parse(declaration.PURL)
		if err != nil {
			return nil, fmt.Errorf("parsing declaration purl %q: %w", declaration.PURL, err)
		}
		result[declaration.Location] = pins.Pin{
			Name:    canonical.Name,
			Version: version,
			PURL:    declaration.PURL,
		}
	}
	return result, nil
}

// parsePypiRanges parses filename's content and returns its range-pinned
// dependencies, keyed the same way as parsePypiPins.
func parsePypiRanges(filename, content string) (map[string]pins.RangePin, error) {
	result := make(map[string]pins.RangePin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse(filename, []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing %s: %w", filename, err)
	}

	for _, declaration := range parsed.Declarations {
		spec, _, _ := strings.Cut(declaration.Version, ";")
		spec = strings.TrimSpace(spec)
		if !pins.IsRange(declaration.Version, scheme, true) {
			continue
		}
		canonical, err := purl.Parse(declaration.PURL)
		if err != nil {
			return nil, fmt.Errorf("parsing declaration purl %q: %w", declaration.PURL, err)
		}
		result[declaration.Location] = pins.RangePin{
			Name: canonical.Name,
			Spec: spec,
			PURL: declaration.PURL,
		}
	}
	return result, nil
}

// formatExactPin renders a latest version as pypi's exact-pin syntax.
func formatExactPin(latest string) string { return "==" + latest }

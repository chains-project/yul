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

// parsePypi parses filename's content (requirements.txt or pyproject.toml)
// and returns its exactly-pinned ("==") and range-pinned dependencies, keyed
// by their source declaration location and named by their canonical PURL
// package name.
func parsePypi(filename, content string) (map[string]pins.Pin, map[string]pins.RangePin, error) {
	exact := make(map[string]pins.Pin)
	ranges := make(map[string]pins.RangePin)
	if strings.TrimSpace(content) == "" {
		return exact, ranges, nil
	}

	parsed, err := manifests.Parse(filename, []byte(content))
	if err != nil {
		return nil, nil, fmt.Errorf("parsing %s: %w", filename, err)
	}

	for _, declaration := range parsed.Declarations {
		version, isExact := pins.ExactVersion(declaration.Version, scheme, true)
		if !isExact && !pins.IsRange(declaration.Version, scheme, true) {
			continue
		}
		canonical, err := purl.Parse(declaration.PURL)
		if err != nil {
			return nil, nil, fmt.Errorf("parsing declaration purl %q: %w", declaration.PURL, err)
		}
		if isExact {
			exact[declaration.Location] = pins.Pin{
				Name:    canonical.Name,
				Version: version,
				PURL:    declaration.PURL,
			}
			continue
		}
		spec, _, _ := strings.Cut(declaration.Version, ";")
		ranges[declaration.Location] = pins.RangePin{
			Name: canonical.Name,
			Spec: strings.TrimSpace(spec),
			PURL: declaration.PURL,
		}
	}
	return exact, ranges, nil
}

// formatExactPin renders a latest version as pypi's exact-pin syntax.
func formatExactPin(latest string) string { return "==" + latest }

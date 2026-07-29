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
// and named by their PEP 503 normalized package name.
func parsePypiPins(filename, content string) (map[string]pins.Pin, error) {
	result := make(map[string]pins.Pin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse(filename, []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing %s: %w", filename, err)
	}

	for _, dep := range parsed.Dependencies {
		version, ok := pins.ExactVersion(dep.Version, scheme, true)
		if !ok {
			continue
		}
		name := normalizePackageName(dep.Name)
		result[name] = pins.Pin{
			Name:    name,
			Version: version,
			PURL:    purl.BuildPURLString(scheme, name, "", ""),
		}
	}
	return result, nil
}

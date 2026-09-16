// Package pypi checks requirements.txt and pyproject.toml for dependencies
// whose version requirement is based on an older version than what's
// actually released, using git-pkgs/manifests to
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
// pyproject.toml) and returns every dependency whose requirement has a
// single base version to keep current — "==", ">=", "~=", or Poetry's "^",
// "~", and bare caret versions — keyed by their source declaration location
// and named by their canonical PURL package name. Exclusions, upper bounds,
// multi-clause ranges like ">=1.0,<2.0", and wildcard pins ("==1.2.*") are
// left alone.
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
		operator, version, ok := pins.ParseSpec(declaration.Version, scheme, true)
		if !ok {
			continue
		}
		canonical, err := purl.Parse(declaration.PURL)
		if err != nil {
			return nil, fmt.Errorf("parsing declaration purl %q: %w", declaration.PURL, err)
		}
		result[declaration.Location] = pins.Pin{
			Name:     canonical.Name,
			Operator: operator,
			Version:  version,
			PURL:     declaration.PURL,
		}
	}
	return result, nil
}

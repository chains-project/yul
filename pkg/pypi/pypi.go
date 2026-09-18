// Package pypi checks requirements.txt and pyproject.toml for dependencies
// pinned older than what's actually released, using git-pkgs/manifests to
// parse manifests and an injected resolver.Resolver to look up latest
// releases.
package pypi

import (
	"fmt"
	"strconv"
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
func parsePypi(filename, content string) (map[string]pins.Pin, error) {
	result := make(map[string]pins.Pin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse(filename, []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing %s: %w", filename, err)
	}

	for _, declaration := range parsed.Declarations {
		version, isExact := pins.ExactVersion(declaration.Version, scheme, true)
		if !isExact && !pins.IsRange(declaration.Version, scheme, true) {
			continue
		}
		canonical, err := purl.Parse(declaration.PURL)
		if err != nil {
			return nil, fmt.Errorf("parsing declaration purl %q: %w", declaration.PURL, err)
		}
		if isExact {
			result[declaration.Location] = pins.Pin{
				Name: canonical.Name,
				Spec: version,
				PURL: declaration.PURL,
			}
			continue
		}
		spec, _, _ := strings.Cut(declaration.Version, ";")
		result[declaration.Location] = pins.Pin{
			Name:  canonical.Name,
			Spec:  strings.TrimSpace(spec),
			PURL:  declaration.PURL,
			Range: true,
		}
	}
	return result, nil
}

// formatRangeFix renders a replacement range that includes latest,
// matching spec's own syntax family: Poetry's caret/tilde/bare-version
// convention (pins.IsPoetryStyle) gets a caret anchored at latest, the
// same as npm/Cargo; PEP 440 (used by requirements.txt and PEP 621
// pyproject tables) has no caret operator, so it gets an explicit
// lower-bound/next-major pair instead, or just the lower bound if latest's
// major version can't be parsed.
func formatRangeFix(spec, latest string) string {
	if pins.IsPoetryStyle(spec) {
		return "^" + latest
	}
	if upperBound, ok := nextMajor(latest); ok {
		return ">=" + latest + ",<" + upperBound
	}
	return ">=" + latest
}

// nextMajor returns "N+1.0.0" for a version's leading major component, or
// ok=false if that component isn't a plain integer.
func nextMajor(version string) (string, bool) {
	major, _, _ := strings.Cut(version, ".")
	n, err := strconv.Atoi(major)
	if err != nil {
		return "", false
	}
	return strconv.Itoa(n+1) + ".0.0", true
}

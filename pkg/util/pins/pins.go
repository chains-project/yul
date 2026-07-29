// Package pins identifies exactly-pinned dependencies in a parsed manifest
// and diffs them against a resolver's view of each package's latest
// release, using git-pkgs/vers for both jobs so ecosystem checkers don't
// reimplement version-range or comparison rules.
package pins

import (
	"context"
	"fmt"
	"strings"

	"github.com/git-pkgs/vers"

	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/chains-project/yul/pkg/util/resolver"
)

// Pin is an exactly-pinned dependency extracted from a manifest, along with
// the PURL to resolve its latest version through.
type Pin struct {
	Namespace string // e.g. Maven groupId; empty for npm/pypi
	Name      string
	Version   string
	PURL      string
}

// ExactVersion reports whether spec pins a package to exactly one version
// under the given vers scheme (e.g. "npm", "pypi"), returning that version.
// Anything looser (a range, a wildcard, a dist-tag, multiple specifiers, an
// exclusion) reports ok=false, since there's nothing exact to compare
// against a latest release.
//
// requireOperator rejects a bare version literal with no leading operator
// at all. pypi needs this: a bare version in a Poetry dependency table
// means a caret range, not an exact pin, whereas npm's package.json treats
// a bare version as exact.
func ExactVersion(spec, scheme string, requireOperator bool) (string, bool) {
	spec, _, _ = strings.Cut(spec, ";") // drop a trailing PEP 508 environment marker
	spec = strings.TrimSpace(spec)
	if spec == "" {
		return "", false
	}
	if requireOperator && !strings.ContainsRune("=<>!~^", rune(spec[0])) {
		return "", false
	}

	normalized := spec
	if scheme == "pypi" {
		// vers's constraint parser only recognizes a single "=" for exact
		// matches; PEP 440's "==" would otherwise leave a stray "=" in the
		// version string.
		normalized = strings.Replace(normalized, "==", "=", 1)
	}

	r, err := vers.ParseNative(normalized, scheme)
	if err != nil {
		return "", false
	}
	if len(r.Exclusions) != 0 || len(r.Intervals) != 1 {
		return "", false
	}

	iv := r.Intervals[0]
	if iv.Min == "" || iv.Max == "" || iv.Min != iv.Max || !iv.MinInclusive || !iv.MaxInclusive {
		return "", false
	}
	// Guards against syntax vers's generic constraint parser accepts as a
	// literal "exact version" only because it doesn't recognize the
	// operator (e.g. Poetry's "^1.2.3" caret syntax under the pypi scheme).
	if !vers.ValidWithScheme(iv.Min, scheme) {
		return "", false
	}
	return iv.Min, true
}

// Diff reports pins in after that are new or whose version changed from
// before, and whose pinned version doesn't match the latest release res
// knows about (compared under scheme's ordering rules). Pins left
// untouched by the write are ignored even if outdated.
func Diff(ctx context.Context, before, after map[string]Pin, scheme string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	var changed []Pin
	for name, pin := range after {
		if prior, ok := before[name]; ok && prior.Version == pin.Version {
			continue // untouched by this write
		}
		changed = append(changed, pin)
	}
	if len(changed) == 0 {
		return nil, nil
	}

	purls := make([]string, len(changed))
	for i, pin := range changed {
		purls[i] = pin.PURL
	}

	latest, err := res.LatestVersions(ctx, purls)
	if err != nil {
		return nil, fmt.Errorf("resolving latest versions: %w", err)
	}

	var mismatches []mismatch.Mismatch
	for _, pin := range changed {
		latestVersion, ok := latest[pin.PURL]
		if !ok {
			return nil, fmt.Errorf("resolving %s: no latest version found", pin.Name)
		}
		if vers.CompareWithScheme(pin.Version, latestVersion, scheme) != 0 {
			mismatches = append(mismatches, mismatch.Mismatch{
				Namespace: pin.Namespace,
				Name:      pin.Name,
				Current:   pin.Version,
				Latest:    latestVersion,
			})
		}
	}
	return mismatches, nil
}

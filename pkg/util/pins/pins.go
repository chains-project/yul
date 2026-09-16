// Package pins identifies dependency version requirements that yul can keep
// current in a parsed manifest and diffs them against a resolver's view of
// each package's latest release, using git-pkgs/vers for version validation
// and comparison so ecosystem checkers don't reimplement those rules.
package pins

import (
	"context"
	"fmt"
	"strings"

	"github.com/git-pkgs/vers"

	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/chains-project/yul/pkg/util/resolver"
)

// Pin is a dependency requirement extracted from a manifest whose base
// version yul can keep current, along with the PURL to resolve its latest
// version through. Operator is the requirement's operator prefix (e.g. "^",
// ">=", "==", or "" for a bare version) and is preserved verbatim when
// suggesting the latest version, so "^0.1.0" is reported as "^0.5.1" rather
// than being collapsed to an exact pin.
type Pin struct {
	Namespace string // e.g. Maven groupId; empty for npm/pypi
	Name      string
	Operator  string
	Version   string
	PURL      string
}

// Spec is the parsed form of a version requirement: a single operator
// applied to a single base version.
type Spec struct {
	Operator string
	Version  string
}

// operators are the requirement operators whose base version can be bumped
// to the latest release without changing what the requirement means: the
// updated requirement still admits the latest release. Longer operators are
// listed first so "==" isn't matched as "=" followed by "=1.2.3". Anything
// else — upper bounds ("<", "<="), exclusions ("!="), strict lower bounds
// (">" would exclude the latest release itself), multi-clause ranges,
// wildcards, dist-tags — has no single base version to update.
var operators = []string{"==", "~=", ">=", "=", "^", "~"}

// ParseSpec reports whether spec is a requirement yul can keep current
// under the given vers scheme (e.g. "npm", "pypi", "cargo"): a single
// supported operator (or none) followed by one valid version. It returns the
// operator and the base version separately, so callers can compare the
// version against the latest release and suggest the same operator with the
// new version.
//
// bareIsRange says how a bare version literal with no operator is
// interpreted. Cargo and Poetry treat "1.2.3" as the caret range "^1.2.3",
// so any valid version is accepted as the base to bump. npm treats a bare
// version as an exact pin, but a partial one like "1.2" is an x-range
// (">=1.2.0 <1.3.0"); bareIsRange=false only accepts a bare version that is
// exact, so such x-ranges are left alone rather than narrowed to a pin.
func ParseSpec(spec, scheme string, bareIsRange bool) (Spec, bool) {
	spec, _, _ = strings.Cut(spec, ";") // drop a trailing PEP 508 environment marker
	spec = strings.TrimSpace(spec)
	if spec == "" {
		return Spec{}, false
	}

	var operator string
	for _, op := range operators {
		if strings.HasPrefix(spec, op) {
			operator = op
			break
		}
	}
	version := strings.TrimSpace(strings.TrimPrefix(spec, operator))
	if version == "" || !vers.ValidWithScheme(version, scheme) {
		return Spec{}, false
	}

	if operator == "" && !bareIsRange {
		r, err := vers.ParseNative(version, scheme)
		if err != nil {
			return Spec{}, false
		}
		if _, exact := r.ExactVersion(); !exact {
			return Spec{}, false
		}
	}
	return Spec{Operator: operator, Version: version}, true
}

// ExactVersion reports whether spec pins a package to exactly one version
// under the given vers scheme, returning that version. It's for ecosystems
// whose manifests have no operator to preserve (go.mod, Maven's hard
// "[1.2.3]" requirement); npm, PyPI, and Cargo go through ParseSpec so a
// range's operator survives the suggestion.
func ExactVersion(spec, scheme string) (string, bool) {
	spec = strings.TrimSpace(spec)
	if spec == "" {
		return "", false
	}
	r, err := vers.ParseNative(spec, scheme)
	if err != nil {
		return "", false
	}
	version, ok := r.ExactVersion()
	if !ok || !vers.ValidWithScheme(version, scheme) {
		return "", false
	}
	return version, true
}

// Diff reports pins in after that are new or whose requirement changed from
// before, and whose base version is older than the latest release res knows
// about (compared under scheme's ordering rules). Pins left untouched by
// the write are ignored even if outdated. Moving a declaration to a
// different logical location counts as a change. Each mismatch's Current
// and Latest carry the pin's operator, so the suggestion keeps the
// requirement's shape.
func Diff(ctx context.Context, before, after map[string]Pin, scheme string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	var changed []Pin
	for location, pin := range after {
		if prior, ok := before[location]; ok && prior == pin {
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
		if vers.CompareWithScheme(pin.Version, latestVersion, scheme) < 0 {
			mismatches = append(mismatches, mismatch.Mismatch{
				Namespace: pin.Namespace,
				Name:      pin.Name,
				Current:   pin.Operator + pin.Version,
				Latest:    pin.Operator + latestVersion,
			})
		}
	}
	return mismatches, nil
}

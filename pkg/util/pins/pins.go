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

// Pin is a dependency extracted from a manifest, pinned to either a single
// exact version or a version range, along with the PURL to resolve its
// latest version through.
type Pin struct {
	Namespace string // e.g. Maven groupId; empty for npm/pypi/cargo
	Name      string
	Version   string // the exact version, or the range exactly as written (e.g. "^4.0.0") when Range is true
	PURL      string
	Range     bool // true when Version is a version range rather than a single exact version
}

// ExactVersion reports whether spec pins a package to exactly one version
// under the given vers scheme (e.g. "npm", "pypi"), returning that version.
// Anything looser (a range, a wildcard, or a dist-tag) reports ok=false,
// since there's nothing exact to compare against a latest release.
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

	r, err := vers.ParseNative(spec, scheme)
	if err != nil {
		return "", false
	}
	version, ok := r.ExactVersion()
	if !ok {
		return "", false
	}

	// Guards against syntax vers's generic constraint parser accepts as a
	// literal "exact version" only because it doesn't recognize the
	// operator (e.g. Poetry's "^1.2.3" caret syntax under the pypi scheme).
	if !vers.ValidWithScheme(version, scheme) {
		return "", false
	}
	return version, true
}

// IsRange reports whether spec is a version range under scheme rather than
// a single exact version or a non-version reference like a dist-tag.
//
// requireOperator matches ExactVersion's flag. A bare version under Poetry
// or Cargo is itself a range (their implicit-caret default), not an exact
// pin.
func IsRange(spec, scheme string, requireOperator bool) bool {
	spec, _, _ = strings.Cut(spec, ";") // drop a trailing PEP 508 environment marker
	spec = strings.TrimSpace(spec)
	if spec == "" {
		return false
	}

	hasOperator := strings.ContainsRune("=<>!~^", rune(spec[0]))
	if requireOperator && !hasOperator && vers.ValidWithScheme(spec, scheme) {
		return true // bare version literal under an implicit-caret default
	}

	r, err := vers.ParseNative(spec, scheme)
	if err != nil {
		return false // not a version constraint at all
	}
	version, ok := r.ExactVersion()
	if !ok {
		return true // genuine range
	}

	// An unrecognized operator (e.g. Poetry's caret under the pypi scheme)
	// parses as a fake "exact version" instead of erroring out. Treat it
	// as a range only if it actually had an operator prefix.
	return hasOperator && !vers.ValidWithScheme(version, scheme)
}

// satisfiesRange reports whether latest satisfies spec under scheme.
//
// Poetry's caret and tilde operators aren't understood by vers's pypi
// scheme, so those specs are rewritten to equivalent npm syntax first,
// since Poetry's caret/tilde semantics match npm's. A "~=" spec is left
// alone since that's PEP 440's own operator, already handled correctly.
func satisfiesRange(latest, spec, scheme string) bool {
	checkScheme, checkSpec := scheme, spec
	if scheme == "pypi" {
		switch {
		case spec == "":
			return false
		case spec[0] == '^':
			checkScheme = "npm"
		case spec[0] == '~' && !strings.HasPrefix(spec, "~="):
			checkScheme = "npm"
		case !strings.ContainsRune("=<>!~^", rune(spec[0])):
			checkScheme, checkSpec = "npm", "^"+spec // Poetry's implicit-caret default
		}
	}
	ok, err := vers.Satisfies(latest, checkSpec, checkScheme)
	return err == nil && ok
}

// Diff reports pins in after that are new or changed from before and need
// attention: an exact pin older than the latest release res knows about
// (compared under scheme's ordering rules), or a range that already
// allows the latest release but has no lockfile alongside the manifest
// (hasLockfile), so the range's actually-installed version isn't pinned
// anywhere. A range that excludes the latest release isn't handled here
// yet. Pins left untouched by the write are ignored even if outdated.
// Moving a declaration to a different logical location counts as a
// change.
func Diff(ctx context.Context, before, after map[string]Pin, scheme string, res resolver.Resolver, hasLockfile bool) ([]mismatch.Mismatch, error) {
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
		if pin.Range {
			if !satisfiesRange(latestVersion, pin.Version, scheme) || hasLockfile {
				continue
			}
			mismatches = append(mismatches, mismatch.Mismatch{
				Namespace:  pin.Namespace,
				Name:       pin.Name,
				Current:    pin.Version,
				Latest:     latestVersion,
				Range:      true,
				NoLockfile: true,
			})
			continue
		}
		if vers.CompareWithScheme(pin.Version, latestVersion, scheme) < 0 {
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

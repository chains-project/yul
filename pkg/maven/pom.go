// Package maven checks pom.xml declarations for versions pinned older than
// what's actually released, using git-pkgs/manifests to parse the POM and an
// injected resolver.Resolver to look up latest releases. It also flags a
// newly added dependency whose groupId:artifactId - or whose pinned
// version - doesn't exist on Maven Central at all, a coordinate the model
// hallucinated, via an injected ExistenceChecker (see existence.go).
package maven

import (
	"context"
	"fmt"
	"strings"

	"github.com/git-pkgs/manifests"

	"github.com/chains-project/yul/pkg/util/mismatch"
	"github.com/chains-project/yul/pkg/util/pins"
	"github.com/chains-project/yul/pkg/util/resolver"
)

const scheme = "maven"

// Checker implements manifestchecker.ManifestChecker for pom.xml.
type Checker struct {
	// Resolver resolves latest released versions. main.go wires up an
	// enrichment-backed resolver; tests inject a fake one.
	Resolver resolver.Resolver

	// Existence flags hallucinated coordinates - a newly added
	// <dependency> whose groupId:artifactId, or whose pinned version, was
	// never published to Maven Central. A nil Existence skips that check,
	// leaving only the outdated-version comparison.
	Existence ExistenceChecker
}

func (Checker) Filename() string { return "pom.xml" }

func (c Checker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckPOM(before, after, c.Resolver, c.Existence)
}

// parsePOMPins returns concrete source-level Maven version declarations keyed
// by their stable location in the POM. Maven commonly uses a bare version as a
// fixed declaration, which is the behavior the hook has historically checked.
func parsePOMPins(content string) (map[string]pins.Pin, error) {
	result := make(map[string]pins.Pin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse("pom.xml", []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing pom.xml: %w", err)
	}

	for _, declaration := range parsed.Declarations {
		version, ok := mavenPinnedVersion(declaration.Version)
		if !ok {
			continue
		}
		namespace, name, ok := strings.Cut(declaration.Name, ":")
		if !ok || namespace == "" || name == "" {
			continue
		}
		result[declaration.Location] = pins.Pin{
			Namespace: namespace,
			Name:      name,
			Version:   version,
			PURL:      declaration.PURL,
		}
	}
	return result, nil
}

func mavenPinnedVersion(requirement string) (string, bool) {
	requirement = strings.TrimSpace(requirement)
	if requirement == "" || strings.Contains(requirement, "${") {
		return "", false
	}
	if strings.HasPrefix(requirement, "[") || strings.HasPrefix(requirement, "(") {
		return pins.ExactVersion(requirement, scheme, false)
	}
	return requirement, true
}

// CheckPOM compares pom.xml content before and after a Write and reports any
// concrete Maven version declaration that is newly added or changed and
// either doesn't match the latest release known to res or - when exist is
// non-nil - names a groupId:artifactId (or a version of one) that doesn't
// exist on Maven Central. Untouched and non-concrete declarations are
// ignored.
func CheckPOM(before, after string, res resolver.Resolver, exist ExistenceChecker) ([]mismatch.Mismatch, error) {
	if res == nil {
		return nil, fmt.Errorf("maven: resolver is nil")
	}
	beforePins, err := parsePOMPins(before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parsePOMPins(after)
	if err != nil {
		return nil, err
	}

	// Existence is checked first: a confirmed-missing pin is dropped from
	// afterPins so the outdated-version pass doesn't then choke trying to
	// resolve a latest version for a package that doesn't exist.
	hallucinated := checkHallucinated(context.Background(), exist, pins.Changed(beforePins, afterPins), afterPins)

	outdated, err := pins.Diff(context.Background(), beforePins, afterPins, scheme, res)
	if err != nil {
		return nil, err
	}
	return append(hallucinated, outdated...), nil
}

// checkHallucinated queries exist for every newly added or changed pin and
// returns a mismatch for each groupId:artifactId Maven Central has no
// record of, or each pinned version that was never published. Flagged pins
// are also deleted from afterPins so the outdated-version pass doesn't then
// try to resolve them. A nil exist disables the check; an inconclusive
// lookup (network error) is skipped, never reported.
func checkHallucinated(ctx context.Context, exist ExistenceChecker, changed, afterPins map[string]pins.Pin) []mismatch.Mismatch {
	if exist == nil || len(changed) == 0 {
		return nil
	}

	var out []mismatch.Mismatch
	for location, pin := range changed {
		ex, err := exist.Existence(ctx, pin.Namespace, pin.Name, pin.Version)
		if err != nil {
			continue // inconclusive: fail open
		}
		switch {
		case !ex.Package:
			out = append(out, mismatch.Mismatch{
				Namespace: pin.Namespace,
				Name:      pin.Name,
				Current:   pin.Version,
				Kind:      mismatch.KindMissingPackage,
			})
			delete(afterPins, location)
		case pin.Version != "" && !ex.Version:
			out = append(out, mismatch.Mismatch{
				Namespace: pin.Namespace,
				Name:      pin.Name,
				Current:   pin.Version,
				Kind:      mismatch.KindMissingVersion,
			})
			delete(afterPins, location)
		}
	}
	return out
}

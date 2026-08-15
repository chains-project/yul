// Package maven checks pom.xml declarations for versions pinned older than
// what's actually released, using git-pkgs/manifests to parse the POM and an
// injected resolver.Resolver to look up latest releases.
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
}

func (Checker) Filename() string { return "pom.xml" }

func (c Checker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckPOM(before, after, c.Resolver)
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
// concrete Maven version declaration that is newly added or changed and does
// not match the latest release known to res. Untouched and non-concrete
// declarations are ignored.
func CheckPOM(before, after string, res resolver.Resolver) ([]mismatch.Mismatch, error) {
	beforePins, err := parsePOMPins(before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parsePOMPins(after)
	if err != nil {
		return nil, err
	}
	return pins.Diff(context.Background(), beforePins, afterPins, scheme, res)
}

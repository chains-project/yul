// Package maven checks pom.xml declarations for versions pinned older than
// what's actually released, using git-pkgs/manifests to parse the POM and an
// injected resolver.Resolver to look up latest releases.
package maven

import (
	"context"
	"encoding/xml"
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
// A version written as a single "${name}" property reference is resolved
// against the POM's own top-level <properties> block, so a pin like
// "${mockito.version}" is checked just like a literal one.
func parsePOMPins(content string) (map[string]pins.Pin, error) {
	result := make(map[string]pins.Pin)
	if strings.TrimSpace(content) == "" {
		return result, nil
	}

	parsed, err := manifests.Parse("pom.xml", []byte(content))
	if err != nil {
		return nil, fmt.Errorf("parsing pom.xml: %w", err)
	}
	props := parsePOMProperties(content)

	for _, declaration := range parsed.Declarations {
		version, ok := mavenPinnedVersion(declaration.Version, props)
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

// pomPropertiesDoc extracts a POM's top-level <properties> block regardless
// of the default xmlns Maven POMs declare on <project> (Go's xml decoder
// matches unqualified struct tags by local name alone).
type pomPropertiesDoc struct {
	Properties struct {
		Entries []struct {
			XMLName xml.Name
			Value   string `xml:",chardata"`
		} `xml:",any"`
	} `xml:"properties"`
}

// parsePOMProperties returns the POM's own <properties> values, keyed by
// element name. It deliberately doesn't resolve parent POMs, profiles, or
// built-in properties like ${project.version}: only what's declared
// directly in this file, matching the rest of this checker's source-level,
// no-network-beyond-the-resolver approach. Malformed XML yields a nil map;
// manifests.Parse above is the one that surfaces parse errors.
func parsePOMProperties(content string) map[string]string {
	var doc pomPropertiesDoc
	if err := xml.Unmarshal([]byte(content), &doc); err != nil {
		return nil
	}
	props := make(map[string]string, len(doc.Properties.Entries))
	for _, entry := range doc.Properties.Entries {
		props[entry.XMLName.Local] = strings.TrimSpace(entry.Value)
	}
	return props
}

func mavenPinnedVersion(requirement string, props map[string]string) (string, bool) {
	requirement = strings.TrimSpace(requirement)
	if requirement == "" {
		return "", false
	}
	if strings.HasPrefix(requirement, "${") && strings.HasSuffix(requirement, "}") &&
		strings.Count(requirement, "${") == 1 {
		name := requirement[2 : len(requirement)-1]
		resolved, ok := props[name]
		if !ok || resolved == "" || strings.Contains(resolved, "${") {
			return "", false
		}
		requirement = resolved
	} else if strings.Contains(requirement, "${") {
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
	return pins.Diff(context.Background(), beforePins, afterPins, scheme, res)
}

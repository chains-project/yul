package pypi

import (
	"fmt"
	"strings"

	"github.com/chains-project/yul/pkg/util/mismatch"
)

// diffPins reports any package whose pin in afterPins is newly added or
// changed from beforePins, and is older than the latest release on PyPI.
// Packages left untouched by the write are ignored even if outdated.
func diffPins(beforePins, afterPins map[string]string) ([]mismatch.Mismatch, error) {
	var mismatches []mismatch.Mismatch
	for name, version := range afterPins {
		if prior, ok := beforePins[name]; ok && prior == version {
			continue // untouched by this write
		}

		latest, err := (Resolver{}).LatestVersion(name)
		if err != nil {
			return nil, fmt.Errorf("resolving %s: %w", name, err)
		}

		if latest != version {
			mismatches = append(mismatches, mismatch.Mismatch{
				Namespace: "",
				Name:      name,
				Current:   version,
				Latest:    latest,
			})
		}
	}
	return mismatches, nil
}

// parseRequirementLine extracts the package name and pinned version from a
// single PEP 508 requirement line (as used in both requirements.txt and
// PEP 621 dependency arrays). ok is true only when the line pins the
// package to exactly one version with "=="; anything looser (>=, ~=, no
// pin, multiple specifiers, a VCS/URL requirement, etc.) reports ok=false
// since there's nothing exact to compare against the latest release.
func parseRequirementLine(line string) (name, version string, ok bool) {
	line, _, _ = strings.Cut(line, "#") // strip inline comment
	line = strings.TrimSpace(line)
	if line == "" || strings.HasPrefix(line, "-") {
		return "", "", false
	}

	// Drop any environment marker, e.g. `; python_version >= "3.8"`.
	line, _, _ = strings.Cut(line, ";")
	line = strings.TrimSpace(line)

	// Multiple specifiers (e.g. ">=1.0,<2.0") aren't an exact pin.
	if strings.Contains(line, ",") {
		return "", "", false
	}

	idx := strings.Index(line, "==")
	if idx == -1 {
		return "", "", false
	}
	// Reject other specifiers that share "=" with "==", e.g. "!=", "~=", ">=", "<=".
	if idx > 0 && strings.ContainsRune("!~<>=", rune(line[idx-1])) {
		return "", "", false
	}

	namePart := strings.TrimSpace(line[:idx])
	namePart, _, _ = strings.Cut(namePart, "[") // drop extras, e.g. "requests[security]"
	namePart = strings.TrimSpace(namePart)
	if namePart == "" {
		return "", "", false
	}

	versionPart := strings.TrimSpace(line[idx+2:])
	if versionPart == "" {
		return "", "", false
	}

	return normalizePackageName(namePart), versionPart, true
}

// normalizePackageName applies PEP 503 normalization so that e.g.
// "My-Package_Name" and "my.package.name" are recognized as the same
// distribution.
func normalizePackageName(name string) string {
	name = strings.ToLower(name)
	var b strings.Builder
	prevSep := false
	for _, r := range name {
		if r == '-' || r == '_' || r == '.' {
			if !prevSep {
				b.WriteByte('-')
			}
			prevSep = true
			continue
		}
		b.WriteRune(r)
		prevSep = false
	}
	return strings.Trim(b.String(), "-")
}

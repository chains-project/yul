package npm

import (
	"encoding/json"
	"fmt"
	"regexp"
	"strings"

	"github.com/chains-project/yul/pkg/util/mismatch"
)

// Checker implements manifestchecker.ManifestChecker for package.json.
type Checker struct{}

func (Checker) Filename() string { return "package.json" }

func (Checker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckPackageJSON(before, after)
}

type packageJSON struct {
	Dependencies         map[string]string `json:"dependencies"`
	DevDependencies      map[string]string `json:"devDependencies"`
	OptionalDependencies map[string]string `json:"optionalDependencies"`
	PeerDependencies     map[string]string `json:"peerDependencies"`
}

// exactVersion matches a bare semver (no range operators, wildcards, tags,
// or protocol prefixes like "npm:", "file:", "workspace:", "git+...").
var exactVersion = regexp.MustCompile(`^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$`)

func parsePackageJSON(content string) (map[string]string, error) {
	pins := make(map[string]string)
	if strings.TrimSpace(content) == "" {
		return pins, nil
	}

	var doc packageJSON
	if err := json.Unmarshal([]byte(content), &doc); err != nil {
		return nil, fmt.Errorf("parsing package.json: %w", err)
	}

	addAll := func(deps map[string]string) {
		for name, version := range deps {
			version = strings.TrimSpace(version)
			if exactVersion.MatchString(version) {
				pins[name] = version
			}
		}
	}
	addAll(doc.Dependencies)
	addAll(doc.DevDependencies)
	addAll(doc.OptionalDependencies)
	addAll(doc.PeerDependencies)

	return pins, nil
}

// CheckPackageJSON compares package.json content before and after a Write
// and reports any exactly-pinned package (no "^", "~", range, wildcard, tag,
// or protocol prefix) across dependencies, devDependencies,
// optionalDependencies, and peerDependencies that is newly added or whose
// pinned version was just changed, and is older than the latest release on
// the npm registry. Packages the write didn't touch, or that aren't pinned
// exactly, are left alone.
func CheckPackageJSON(before, after string) ([]mismatch.Mismatch, error) {
	beforePins, err := parsePackageJSON(before)
	if err != nil {
		return nil, err
	}
	afterPins, err := parsePackageJSON(after)
	if err != nil {
		return nil, err
	}

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

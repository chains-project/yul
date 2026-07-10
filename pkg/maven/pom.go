package maven

import (
	"encoding/xml"
	"fmt"
	"strings"

	"github.com/chains-project/yul/pkg/util/mismatch"
)

// Checker implements manifestchecker.ManifestChecker for pom.xml.
type Checker struct{}

func (Checker) Filename() string { return "pom.xml" }

func (Checker) Check(before, after string) ([]mismatch.Mismatch, error) {
	return CheckPOM(before, after)
}

type pomProject struct {
	Dependencies []pomDependency `xml:"dependencies>dependency"`
}

type pomDependency struct {
	GroupID    string `xml:"groupId"`
	ArtifactID string `xml:"artifactId"`
	Version    string `xml:"version"`
}

func parsePOM(content string) (map[string]pomDependency, error) {
	if strings.TrimSpace(content) == "" {
		return map[string]pomDependency{}, nil
	}
	var project pomProject
	if err := xml.Unmarshal([]byte(content), &project); err != nil {
		return nil, fmt.Errorf("parsing pom.xml: %w", err)
	}

	deps := make(map[string]pomDependency, len(project.Dependencies))
	for _, dep := range project.Dependencies {
		deps[dep.GroupID+":"+dep.ArtifactID] = dep
	}
	return deps, nil
}

// CheckPOM compares pom.xml content before and after a Write and reports any
// dependency that is newly added or whose version was just changed, and is
// pinned older than the latest release on Maven Central. Dependencies the
// write didn't touch are left alone, even if outdated.
func CheckPOM(before, after string) ([]mismatch.Mismatch, error) {
	beforeDeps, err := parsePOM(before)
	if err != nil {
		return nil, err
	}
	afterDeps, err := parsePOM(after)
	if err != nil {
		return nil, err
	}

	var mismatches []mismatch.Mismatch
	for key, dep := range afterDeps {
		if dep.Version == "" {
			continue
		}

		if prior, ok := beforeDeps[key]; ok && prior.Version == dep.Version {
			continue // untouched by this write
		}

		latest, err := (Resolver{}).LatestVersion(dep.GroupID, dep.ArtifactID)
		if err != nil {
			return nil, fmt.Errorf("resolving %s:%s: %w", dep.GroupID, dep.ArtifactID, err)
		}

		if latest != dep.Version {
			mismatches = append(mismatches, mismatch.Mismatch{
				Namespace: dep.GroupID,
				Name:      dep.ArtifactID,
				Current:   dep.Version,
				Latest:    latest,
			})
		}
	}

	return mismatches, nil
}

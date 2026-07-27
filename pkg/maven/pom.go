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

// pomCoordinate is the groupId/artifactId/version triple shared by every
// place a Maven coordinate can be pinned: dependencies, plugins, extensions,
// and the parent element. Version is often empty here by design - e.g. a
// <dependency> managed by a <dependencyManagement> block (in this POM or an
// inherited parent) omits its own <version> - so an empty Version means
// "not pinned at this location", not a malformed entry.
type pomCoordinate struct {
	GroupID    string `xml:"groupId"`
	ArtifactID string `xml:"artifactId"`
	Version    string `xml:"version"`
}

// pomPlugin is a <plugin> entry, which may itself pin dependencies (e.g. a
// plugin's runtime classpath additions).
type pomPlugin struct {
	pomCoordinate
	Dependencies []pomCoordinate `xml:"dependencies>dependency"`
}

// pomBuild covers every coordinate-bearing element nested under <build>,
// including the <pluginManagement> variant that only pins versions.
type pomBuild struct {
	Plugins          []pomPlugin     `xml:"plugins>plugin"`
	PluginManagement []pomPlugin     `xml:"pluginManagement>plugins>plugin"`
	Extensions       []pomCoordinate `xml:"extensions>extension"`
}

// pomProfile mirrors the subset of <project> that can also appear inside
// <profiles><profile>: profile-scoped dependencies and plugins are pinned
// the same way as the top-level ones.
type pomProfile struct {
	Dependencies         []pomCoordinate `xml:"dependencies>dependency"`
	DependencyManagement []pomCoordinate `xml:"dependencyManagement>dependencies>dependency"`
	Build                pomBuild        `xml:"build"`
}

type pomProject struct {
	Parent               pomCoordinate   `xml:"parent"`
	Dependencies         []pomCoordinate `xml:"dependencies>dependency"`
	DependencyManagement []pomCoordinate `xml:"dependencyManagement>dependencies>dependency"`
	Build                pomBuild        `xml:"build"`
	Profiles             []pomProfile    `xml:"profiles>profile"`
}

// coordEntry is a single pinned coordinate plus a key that distinguishes
// which kind of element it came from, so a groupId:artifactId that appears
// as both a dependency and a plugin (or in a profile) is tracked separately.
type coordEntry struct {
	kind string
	pomCoordinate
}

func (e coordEntry) key() string {
	return e.kind + ":" + e.GroupID + ":" + e.ArtifactID
}

func collectBuild(kindPrefix string, b pomBuild, out *[]coordEntry) {
	for _, p := range b.Plugins {
		*out = append(*out, coordEntry{kindPrefix + "plugin", p.pomCoordinate})
		for _, d := range p.Dependencies {
			*out = append(*out, coordEntry{kindPrefix + "plugin-dependency", d})
		}
	}
	for _, p := range b.PluginManagement {
		*out = append(*out, coordEntry{kindPrefix + "managed-plugin", p.pomCoordinate})
	}
	for _, e := range b.Extensions {
		*out = append(*out, coordEntry{kindPrefix + "extension", e})
	}
}

func collectCoordinates(project pomProject) []coordEntry {
	var out []coordEntry

	out = append(out, coordEntry{"parent", project.Parent})
	for _, d := range project.Dependencies {
		out = append(out, coordEntry{"dependency", d})
	}
	for _, d := range project.DependencyManagement {
		out = append(out, coordEntry{"managed-dependency", d})
	}
	collectBuild("", project.Build, &out)

	for i, prof := range project.Profiles {
		prefix := fmt.Sprintf("profile[%d]-", i)
		for _, d := range prof.Dependencies {
			out = append(out, coordEntry{prefix + "dependency", d})
		}
		for _, d := range prof.DependencyManagement {
			out = append(out, coordEntry{prefix + "managed-dependency", d})
		}
		collectBuild(prefix, prof.Build, &out)
	}

	return out
}

func parsePOM(content string) (map[string]coordEntry, error) {
	if strings.TrimSpace(content) == "" {
		return map[string]coordEntry{}, nil
	}
	var project pomProject
	if err := xml.Unmarshal([]byte(content), &project); err != nil {
		return nil, fmt.Errorf("parsing pom.xml: %w", err)
	}

	entries := make(map[string]coordEntry)
	for _, e := range collectCoordinates(project) {
		if e.GroupID == "" && e.ArtifactID == "" {
			continue // unset element, e.g. no <parent>
		}
		entries[e.key()] = e
	}
	return entries, nil
}

// CheckPOM compares pom.xml content before and after a Write and reports any
// pinned Maven coordinate - a dependency, a plugin, a build extension, the
// parent, or any of these declared inside a <profile> or a *Management
// block - that is newly added or whose version was just changed, and is
// pinned older than the latest release on Maven Central. Coordinates the
// write didn't touch are left alone, even if outdated.
func CheckPOM(before, after string) ([]mismatch.Mismatch, error) {
	beforeCoords, err := parsePOM(before)
	if err != nil {
		return nil, err
	}
	afterCoords, err := parsePOM(after)
	if err != nil {
		return nil, err
	}

	var mismatches []mismatch.Mismatch
	for key, coord := range afterCoords {
		if coord.Version == "" {
			// No version pinned at this location - inherited from a
			// dependencyManagement block (here or in a parent POM) rather
			// than a blank/malformed entry. Nothing to compare here.
			continue
		}

		if prior, ok := beforeCoords[key]; ok && prior.Version == coord.Version {
			continue // untouched by this write
		}

		latest, err := (Resolver{}).LatestVersion(coord.GroupID, coord.ArtifactID)
		if err != nil {
			return nil, fmt.Errorf("resolving %s:%s: %w", coord.GroupID, coord.ArtifactID, err)
		}

		if latest != coord.Version {
			mismatches = append(mismatches, mismatch.Mismatch{
				Namespace: coord.GroupID,
				Name:      coord.ArtifactID,
				Current:   coord.Version,
				Latest:    latest,
			})
		}
	}

	return mismatches, nil
}

// Package scan walks a project directory and reports every exactly-pinned
// dependency across all known manifest kinds that is pinned older than the
// latest release, not just ones a Write/Edit just touched. It reuses each
// ecosystem's manifestchecker.Check by diffing against an empty "before",
// which makes every pin in the file count as new.
package scan

import (
	"io/fs"
	"os"
	"path/filepath"
	"sort"

	"github.com/chains-project/yul/pkg/util/manifestchecker"
	"github.com/chains-project/yul/pkg/util/mismatch"
)

// Finding is a mismatch.Mismatch located in a specific manifest file.
type Finding struct {
	File string
	mismatch.Mismatch
}

// skipDirs are directories never worth descending into: they hold
// dependencies' own manifests (vendored copies, installed packages), not
// the project's.
var skipDirs = map[string]bool{
	"node_modules": true,
	"vendor":       true,
	"target":       true,
	"dist":         true,
	"build":        true,
	"venv":         true,
	".venv":        true,
	"__pycache__":  true,
}

// Dir walks root and reports a Finding for every exactly-pinned dependency,
// across every manifest kind checkers know about, that's pinned older than
// the latest release. Files a checker can't parse or that a resolver can't
// look up are skipped rather than failing the whole scan, since one bad
// manifest shouldn't hide findings from the rest of the project.
func Dir(root string, checkers []manifestchecker.ManifestChecker) ([]Finding, error) {
	var findings []Finding

	err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return nil // unreadable entry: skip it, don't abort the scan
		}
		base := d.Name()
		if d.IsDir() {
			if path != root && (skipDirs[base] || (base[0] == '.' && base != ".github")) {
				return filepath.SkipDir
			}
			return nil
		}

		checker := checkerFor(checkers, path)
		if checker == nil {
			return nil
		}

		content, err := os.ReadFile(path)
		if err != nil {
			return nil
		}

		rel, err := filepath.Rel(root, path)
		if err != nil {
			rel = path
		}

		mismatches, err := checker.Check("", string(content))
		if err != nil {
			return nil // resolver/parse error on this file: fail open, keep scanning
		}
		for _, m := range mismatches {
			findings = append(findings, Finding{File: rel, Mismatch: m})
		}
		return nil
	})
	if err != nil {
		return nil, err
	}

	sort.Slice(findings, func(i, j int) bool {
		if findings[i].File != findings[j].File {
			return findings[i].File < findings[j].File
		}
		return findings[i].Name < findings[j].Name
	})
	return findings, nil
}

// checkerFor mirrors main.checkerFor: most checkers claim a fixed basename,
// a manifestchecker.PathMatcher (e.g. GitHub Actions workflows) is tried
// against the full path first.
func checkerFor(checkers []manifestchecker.ManifestChecker, path string) manifestchecker.ManifestChecker {
	base := filepath.Base(path)
	for _, c := range checkers {
		if pm, ok := c.(manifestchecker.PathMatcher); ok {
			if pm.MatchesPath(path) {
				return c
			}
			continue
		}
		if c.Filename() == base {
			return c
		}
	}
	return nil
}

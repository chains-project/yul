// Package scan walks a project directory and reports every exactly-pinned
// dependency across all known manifest kinds that is pinned older than the
// latest release, not just ones a Write/Edit just touched. It reuses each
// ecosystem's manifestchecker.Check by diffing against an empty "before",
// which makes every pin in the file count as new.
package scan

import (
	"crypto/sha256"
	"encoding/hex"
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

// manifest is a matched manifest file found while walking a project.
type manifest struct {
	rel     string
	checker manifestchecker.ManifestChecker
	content []byte
}

// walk finds every file under root that some checker owns, skipping
// dependency/build directories that hold other projects' manifests, not
// this project's.
func walk(root string, checkers []manifestchecker.ManifestChecker) ([]manifest, error) {
	var found []manifest

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

		found = append(found, manifest{rel: rel, checker: checker, content: content})
		return nil
	})
	if err != nil {
		return nil, err
	}

	sort.Slice(found, func(i, j int) bool { return found[i].rel < found[j].rel })
	return found, nil
}

// Dir walks root and reports a Finding for every exactly-pinned dependency,
// across every manifest kind checkers know about, that's pinned older than
// the latest release. Files a checker can't parse or that a resolver can't
// look up are skipped rather than failing the whole scan, since one bad
// manifest shouldn't hide findings from the rest of the project.
func Dir(root string, checkers []manifestchecker.ManifestChecker) ([]Finding, error) {
	manifests, err := walk(root, checkers)
	if err != nil {
		return nil, err
	}

	var findings []Finding
	for _, m := range manifests {
		mismatches, err := m.checker.Check("", string(m.content))
		if err != nil {
			continue // resolver/parse error on this file: fail open, keep scanning
		}
		for _, mm := range mismatches {
			findings = append(findings, Finding{File: m.rel, Mismatch: mm})
		}
	}

	sort.Slice(findings, func(i, j int) bool {
		if findings[i].File != findings[j].File {
			return findings[i].File < findings[j].File
		}
		return findings[i].Name < findings[j].Name
	})
	return findings, nil
}

// Hash fingerprints the content of every manifest file checkers would look
// at under root, with no network calls. A cached scan is only safe to reuse
// if this matches the hash from when the cache was written — otherwise a
// manifest edited outside a Write/Edit (e.g. by hand, or by git) would keep
// reporting stale findings until the cache's TTL happens to expire.
func Hash(root string, checkers []manifestchecker.ManifestChecker) (string, error) {
	manifests, err := walk(root, checkers)
	if err != nil {
		return "", err
	}

	h := sha256.New()
	for _, m := range manifests {
		h.Write([]byte(m.rel))
		h.Write([]byte{0})
		h.Write(m.content)
		h.Write([]byte{0})
	}
	return hex.EncodeToString(h.Sum(nil)), nil
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

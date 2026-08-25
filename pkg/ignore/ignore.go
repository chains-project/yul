// Package ignore reads a project's .yul-ignore file: an explicit,
// user-maintained record of exact dependency pins the project has decided
// to keep despite being older than the latest release, so the hook stops
// re-blocking a write the user has already declined once.
package ignore

import (
	"bufio"
	"os"
	"path/filepath"
	"strings"
)

// Filename is the ignore file's name, expected at a project's root
// (the hook's session cwd).
const Filename = ".yul-ignore"

// Set is the collection of pins a project has chosen to keep, keyed by
// "<purl>@<version>" (e.g. "pkg:npm/lodash@4.17.20").
type Set map[string]bool

// Load reads dir/.yul-ignore. A missing file is not an error: it just
// means nothing is ignored, so a project without one behaves exactly as
// it did before this package existed.
func Load(dir string) Set {
	set := make(Set)
	if dir == "" {
		return set
	}

	f, err := os.Open(filepath.Join(dir, Filename))
	if err != nil {
		return set
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		set[line] = true
	}
	return set
}

// Contains reports whether the exact pin of purl (version-less, e.g.
// "pkg:npm/lodash") at version has been marked ignored.
func (s Set) Contains(purl, version string) bool {
	if purl == "" || version == "" {
		return false
	}
	return s[purl+"@"+version]
}

// Package manifestchecker defines the interface each ecosystem package
// implements so the hook can stay ecosystem-agnostic: given a manifest
// filename it owns (e.g. "pom.xml"), compare its content before/after a
// write and report any newly added/changed dependency pinned older than
// what's actually released.
package manifestchecker

import (
	"os"
	"path/filepath"

	"github.com/chains-project/yul/pkg/util/mismatch"
)

type ManifestChecker interface {
	// Filename is the manifest basename this checker handles, e.g. "pom.xml".
	Filename() string

	// Check compares manifest content before and after a write and returns
	// mismatches for dependencies that were newly added/changed by it.
	// hasLockfile reports whether a lockfile this checker's ecosystem
	// recognizes (see LockfileAware) already exists alongside the
	// manifest; a checker with no lockfile convention ignores it.
	Check(before, after string, hasLockfile bool) ([]mismatch.Mismatch, error)
}

// LockfileAware is implemented by a ManifestChecker whose ecosystem has a
// lockfile convention worth checking for alongside a version range (e.g.
// package-lock.json for package.json). Checkers without one - Maven,
// GitHub Actions, go.mod (every entry there is already an exact pin), and
// requirements.txt (no lockfile convention of its own) - don't implement
// it.
type LockfileAware interface {
	// LockfileNames lists the lockfile basenames that count as "present"
	// for this ecosystem, checked in the manifest's own directory.
	LockfileNames() []string
}

// HasLockfile reports whether checker's ecosystem has a lockfile present
// in dir. A checker that doesn't implement LockfileAware reports true
// unconditionally, since there's nothing to check for it - this keeps
// callers from needing their own type switch.
func HasLockfile(dir string, checker ManifestChecker) bool {
	la, ok := checker.(LockfileAware)
	if !ok {
		return true
	}
	for _, name := range la.LockfileNames() {
		if _, err := os.Stat(filepath.Join(dir, name)); err == nil {
			return true
		}
	}
	return false
}

// PathMatcher is implemented by a ManifestChecker whose manifest can't be
// identified by a fixed basename alone, e.g. GitHub Actions workflow files,
// which live under .github/workflows/ but can have any filename. The
// dispatcher tries this before falling back to an exact Filename() match.
type PathMatcher interface {
	// MatchesPath reports whether path (as passed to the hook, typically
	// absolute) is a manifest this checker owns.
	MatchesPath(path string) bool
}

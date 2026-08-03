// Package manifestchecker defines the interface each ecosystem package
// implements so the hook can stay ecosystem-agnostic: given a manifest
// filename it owns (e.g. "pom.xml"), compare its content before/after a
// write and report any newly added/changed dependency pinned older than
// what's actually released.
package manifestchecker

import "github.com/chains-project/yul/pkg/util/mismatch"

type ManifestChecker interface {
	// Filename is the manifest basename this checker handles, e.g. "pom.xml".
	Filename() string

	// Check compares manifest content before and after a write and returns
	// mismatches for dependencies that were newly added/changed by it.
	Check(before, after string) ([]mismatch.Mismatch, error)
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

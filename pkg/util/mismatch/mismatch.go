// Package mismatch defines the shared result type ecosystem manifest
// checkers report back to the hook: a dependency that was just added or
// changed and is pinned older than what's actually released.
package mismatch

type Mismatch struct {
	Namespace string
	Name      string
	Current   string
	Latest    string

	// Suggested is a commit SHA to pin to instead of Latest, or "" if none
	// applies (e.g. GitHub Actions' `@<sha> # <tag>` pin convention).
	Suggested string

	// Range is true when Current is a version range rather than a single
	// pinned version.
	Range bool

	// NoLockfile is true for a Range mismatch whose ecosystem has a
	// lockfile convention (npm, Cargo, Poetry/uv/pdm) but none was found
	// next to the manifest, so the range's actually-installed version
	// isn't pinned anywhere.
	NoLockfile bool
}

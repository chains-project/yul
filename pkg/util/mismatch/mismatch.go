// Package mismatch defines the shared result type ecosystem manifest
// checkers report back to the hook: a dependency that was just added or
// changed and is pinned older than what's actually released.
package mismatch

type Mismatch struct {
	Namespace string
	Name      string
	Current   string
	Latest    string

	// Suggested is a fully-formatted replacement to pin to instead of
	// Latest, or "" if none applies. For GitHub Actions this is a commit
	// SHA. For a Range finding it's Latest in the ecosystem's exact-pin
	// syntax.
	Suggested string

	// Range is true when Current is a version range rather than a single
	// pinned version. Suggested is only set (a replacement range) when the
	// range actually excludes Latest; a Range mismatch with Suggested ==
	// "" means the range already allows Latest and NoLockfile is what's
	// being reported instead.
	Range bool

	// NoLockfile is true for a Range mismatch whose ecosystem has a
	// lockfile convention (npm, Cargo, Poetry/uv/pdm) but none was found
	// next to the manifest, so the range's actually-installed version
	// isn't pinned anywhere.
	NoLockfile bool
}

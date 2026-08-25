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

	// PURL is the version-less package URL identifying the dependency
	// (e.g. "pkg:npm/lodash"), or "" if the checker has none to offer.
	// Combined with Current, "<PURL>@<Current>" is the key a .yul-ignore
	// entry (see pkg/ignore) matches to suppress this mismatch.
	PURL string
}

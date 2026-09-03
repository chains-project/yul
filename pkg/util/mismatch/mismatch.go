// Package mismatch defines the shared result type ecosystem manifest
// checkers report back to the hook: a dependency that was just added or
// changed and is either pinned older than what's actually released, or
// points at a package (or version) that doesn't exist in the registry at
// all - a coordinate the model hallucinated.
package mismatch

// Kind says why a dependency was flagged.
type Kind int

const (
	// KindOutdated is a dependency pinned older than the latest release.
	// It is the zero value, so a Mismatch built without setting Kind is an
	// outdated-version report and Latest holds the version to move to.
	KindOutdated Kind = iota

	// KindMissingPackage is a dependency whose package doesn't exist in
	// the registry at all - a hallucinated coordinate. Latest and
	// Suggested are empty; there's nothing to move to.
	KindMissingPackage

	// KindMissingVersion is a dependency whose package exists but whose
	// pinned version was never published - a hallucinated version. Latest
	// and Suggested are empty.
	KindMissingVersion
)

type Mismatch struct {
	Namespace string
	Name      string
	Current   string
	Latest    string

	// Suggested is a commit SHA to pin to instead of Latest, or "" if none
	// applies (e.g. GitHub Actions' `@<sha> # <tag>` pin convention).
	Suggested string

	// Kind says why this dependency was flagged. The zero value,
	// KindOutdated, means Current is older than Latest. For the
	// KindMissing* kinds there is no newer version to point at.
	Kind Kind
}

// Package mismatch defines the shared result type ecosystem manifest
// checkers report back to the hook: a dependency that was just added or
// changed and is pinned older than what's actually released.
package mismatch

type Mismatch struct {
	Namespace string
	Name      string
	Current   string
	Latest    string

	// Suggested, when non-empty, is the exact text to replace the pin with
	// instead of Latest - for ecosystems where the bare latest version
	// isn't itself the correct replacement (e.g. GitHub Actions'
	// `@<sha> # <tag>` pin convention, where Suggested carries the
	// resolved commit SHA alongside the tag).
	Suggested string
}

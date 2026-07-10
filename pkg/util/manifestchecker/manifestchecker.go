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

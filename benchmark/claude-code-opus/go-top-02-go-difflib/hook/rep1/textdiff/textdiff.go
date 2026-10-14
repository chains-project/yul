// Package textdiff computes unified diffs between two pieces of text.
package textdiff

import (
	"fmt"

	udiff "github.com/aymanbagabas/go-udiff"
)

// DefaultContext is the number of unchanged lines shown around each change.
const DefaultContext = udiff.DefaultContextLines

// Unified returns a unified diff transforming want into got, labelled with
// the given names. It returns "" if the inputs are identical.
func Unified(wantName, gotName, want, got string) string {
	return udiff.Unified(wantName, gotName, want, got)
}

// UnifiedContext is like Unified but with a configurable number of context lines.
func UnifiedContext(wantName, gotName, want, got string, context int) (string, error) {
	if context < 0 {
		return "", fmt.Errorf("textdiff: negative context %d", context)
	}
	edits := udiff.Lines(want, got)
	if len(edits) == 0 {
		return "", nil
	}
	return udiff.ToUnified(wantName, gotName, want, edits, context)
}

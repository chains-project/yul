// Package textdiff computes unified diffs between two pieces of text.
package textdiff

import (
	"fmt"

	udiff "github.com/aymanbagabas/go-udiff"
)

// DefaultContext is the number of unchanged lines shown around each hunk.
const DefaultContext = udiff.DefaultContextLines

// Unified returns a unified diff turning want into got, labelled with
// wantName and gotName. It returns "" if the inputs are identical.
func Unified(wantName, gotName, want, got string) string {
	return udiff.Unified(wantName, gotName, want, got)
}

// UnifiedContext is like Unified but shows context lines of surrounding
// unchanged text around each hunk.
func UnifiedContext(wantName, gotName, want, got string, context int) (string, error) {
	if context < 0 {
		return "", fmt.Errorf("textdiff: negative context %d", context)
	}
	edits := udiff.Lines(want, got)
	return udiff.ToUnified(wantName, gotName, want, edits, context)
}

// TB is the subset of testing.TB used by Check.
type TB interface {
	Helper()
	Errorf(format string, args ...any)
}

// Check reports a test error with a unified diff if got differs from want.
// It returns true if they are equal.
func Check(t TB, want, got string) bool {
	t.Helper()
	if d := Unified("want", "got", want, got); d != "" {
		t.Errorf("mismatch (-want +got):\n%s", d)
		return false
	}
	return true
}

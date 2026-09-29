// Package diff computes and renders unified diffs between two pieces of text.
//
// It is intended to be embedded in testing tools that need to show what
// changed between an expected value and an actual value.
package diff

import (
	"github.com/pmezard/go-difflib/difflib"
)

// DefaultContext is the number of unchanged lines rendered around each change
// when Options.Context is not set.
const DefaultContext = 3

// Options controls how a unified diff is rendered.
type Options struct {
	// FromFile and ToFile are the labels printed in the ---/+++ headers.
	FromFile string
	ToFile   string

	// FromDate and ToDate are optional timestamps printed after the file
	// labels in the ---/+++ headers.
	FromDate string
	ToDate   string

	// Context is the number of unchanged lines rendered around each change.
	// Values less than or equal to zero use DefaultContext.
	Context int
}

// Unified renders a unified diff between oldText and newText using the default
// number of context lines. The returned string is empty when the inputs are
// identical.
func Unified(oldText, newText string) (string, error) {
	return UnifiedWithOptions(oldText, newText, Options{})
}

// UnifiedWithOptions renders a unified diff between oldText and newText using
// the supplied Options.
func UnifiedWithOptions(oldText, newText string, opts Options) (string, error) {
	context := opts.Context
	if context <= 0 {
		context = DefaultContext
	}

	ud := difflib.UnifiedDiff{
		A:        difflib.SplitLines(oldText),
		B:        difflib.SplitLines(newText),
		FromFile: opts.FromFile,
		ToFile:   opts.ToFile,
		FromDate: opts.FromDate,
		ToDate:   opts.ToDate,
		Context:  context,
		Eol:      "\n",
	}
	return difflib.GetUnifiedDiffString(ud)
}

// Equal reports whether oldText and newText are identical.
func Equal(oldText, newText string) bool {
	return oldText == newText
}

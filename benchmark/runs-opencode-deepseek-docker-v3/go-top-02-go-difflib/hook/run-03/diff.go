// Package difftool computes and renders unified diffs between two texts.
//
// It is intended to be used by testing tools that want to show a readable
// representation of how two pieces of text differ.
package difftool

import (
	"strings"

	"github.com/pmezard/go-difflib/difflib"
)

// DefaultContext is the number of unchanged lines shown around each change
// when Options.Context is left at its zero value.
const DefaultContext = 3

// Options controls how a unified diff is rendered.
type Options struct {
	// FromFile and ToFile are the labels printed in the --- and +++ headers.
	FromFile string
	ToFile   string
	// FromDate and ToDate are optional timestamps for the headers.
	FromDate string
	ToDate   string
	// Context is the number of unchanged lines surrounding each hunk.
	// A zero value selects DefaultContext.
	Context int
	// Eol is the line terminator used in the output. A zero value selects "\n".
	Eol string
}

// Unified returns a unified diff between texts a and b, using opts to control
// the output. The result is empty when the two texts are identical.
func Unified(a, b string, opts Options) (string, error) {
	context := opts.Context
	if context <= 0 {
		context = DefaultContext
	}
	eol := opts.Eol
	if eol == "" {
		eol = "\n"
	}

	return difflib.GetUnifiedDiffString(difflib.UnifiedDiff{
		A:        splitLines(a),
		B:        splitLines(b),
		FromFile: opts.FromFile,
		FromDate: opts.FromDate,
		ToFile:   opts.ToFile,
		ToDate:   opts.ToDate,
		Context:  context,
		Eol:      eol,
	})
}

// splitLines turns text into difflib's line representation. A single trailing
// newline is trimmed first because difflib.SplitLines normalizes the final
// line to end with an EOL, which would otherwise introduce a phantom empty
// line for newline-terminated text.
func splitLines(s string) []string {
	return difflib.SplitLines(strings.TrimSuffix(s, "\n"))
}

// UnifiedText returns a unified diff between a and b using the default options
// and the labels "a" and "b".
func UnifiedText(a, b string) (string, error) {
	return Unified(a, b, Options{FromFile: "a", ToFile: "b"})
}

// Package udiff computes and renders unified diffs between two texts.
package udiff

import (
	"io"

	"github.com/pmezard/go-difflib/difflib"
)

// DefaultContext is the number of unchanged lines shown around each change
// when Options.Context is not set.
const DefaultContext = 3

// Options controls how a unified diff is rendered. A nil *Options is valid
// and uses the defaults: FromFile "a", ToFile "b" and DefaultContext.
type Options struct {
	// FromFile and ToFile are the labels used in the "---" and "+++" headers.
	FromFile string
	ToFile   string
	// Context is the number of context lines; values <= 0 use DefaultContext.
	Context int
}

func (o *Options) normalize() (from, to string, context int) {
	from, to, context = "a", "b", DefaultContext
	if o == nil {
		return from, to, context
	}
	if o.FromFile != "" {
		from = o.FromFile
	}
	if o.ToFile != "" {
		to = o.ToFile
	}
	if o.Context > 0 {
		context = o.Context
	}
	return from, to, context
}

// Unified returns the unified diff between a and b. It returns an empty
// string when a and b are identical.
func Unified(a, b string, opts *Options) (string, error) {
	from, to, context := opts.normalize()
	return difflib.GetUnifiedDiffString(difflib.UnifiedDiff{
		A:        difflib.SplitLines(a),
		B:        difflib.SplitLines(b),
		FromFile: from,
		ToFile:   to,
		Context:  context,
	})
}

// WriteUnified writes the unified diff between a and b to w. It reports the
// number of bytes written and writes nothing when a and b are identical.
func WriteUnified(w io.Writer, a, b string, opts *Options) (int, error) {
	s, err := Unified(a, b, opts)
	if err != nil {
		return 0, err
	}
	if s == "" {
		return 0, nil
	}
	return io.WriteString(w, s)
}

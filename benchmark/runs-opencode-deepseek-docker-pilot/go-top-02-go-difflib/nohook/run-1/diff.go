// Package difftool computes and renders unified diffs between two
// pieces of text. It is intended for testing helpers that need to
// present expected and actual values in a readable, git-style format.
package difftool

import (
	"fmt"
	"io"
	"strings"

	"github.com/pmezard/go-difflib/difflib"
)

// DefaultContext is the number of unchanged lines shown around each
// change when Options.Context is unset.
const DefaultContext = 3

// Options controls how a unified diff is rendered. The zero value is
// ready to use and produces a diff labelled "expected" and "actual".
type Options struct {
	// FromFile labels the first ("-") side of the diff. It defaults to
	// "expected".
	FromFile string
	// ToFile labels the second ("+") side of the diff. It defaults to
	// "actual".
	ToFile string
	// Context is the number of unchanged lines shown around each
	// change. Non-positive values select DefaultContext.
	Context int
}

// Unified returns a unified diff between a and b using default
// options. It returns an empty string when a and b are identical.
func Unified(a, b string) string {
	s, _ := Render(Options{}, a, b)
	return s
}

// Render returns a unified diff between a and b. The result is empty
// when a and b are identical.
func Render(opts Options, a, b string) (string, error) {
	var sb strings.Builder
	if err := Write(&sb, opts, a, b); err != nil {
		return "", err
	}
	return sb.String(), nil
}

// Write writes a unified diff between a and b to w. It writes nothing
// when a and b are identical.
func Write(w io.Writer, opts Options, a, b string) error {
	diff := difflib.UnifiedDiff{
		A:        splitLines(a),
		B:        splitLines(b),
		FromFile: orDefault(opts.FromFile, "expected"),
		ToFile:   orDefault(opts.ToFile, "actual"),
		Context:  contextLines(opts.Context),
	}
	s, err := difflib.GetUnifiedDiffString(diff)
	if err != nil {
		return fmt.Errorf("difftool: render unified diff: %w", err)
	}
	_, err = io.WriteString(w, s)
	return err
}

func orDefault(s, fallback string) string {
	if s == "" {
		return fallback
	}
	return s
}

func contextLines(n int) int {
	if n <= 0 {
		return DefaultContext
	}
	return n
}

// splitLines splits s into lines that each keep their trailing
// newline, unlike difflib.SplitLines, which appends a spurious blank
// line when s already ends in a newline. A final line without a
// newline is terminated so the rendered diff stays well formed; the
// presence of a trailing newline is therefore not significant.
func splitLines(s string) []string {
	if s == "" {
		return nil
	}
	lines := strings.SplitAfter(s, "\n")
	if lines[len(lines)-1] == "" {
		return lines[:len(lines)-1]
	}
	lines[len(lines)-1] += "\n"
	return lines
}

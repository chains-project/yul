package difftool

import (
	"io"
	"strings"

	"github.com/pmezard/go-difflib/difflib"
)

const DefaultContext = 3

type Options struct {
	FromFile string
	ToFile   string
	FromDate string
	ToDate   string
	Context  int
}

func Unified(from, to string, opts Options) (string, error) {
	if opts.Context == 0 {
		opts.Context = DefaultContext
	}
	return difflib.GetUnifiedDiffString(difflib.UnifiedDiff{
		A:        splitLines(from),
		B:        splitLines(to),
		FromFile: opts.FromFile,
		ToFile:   opts.ToFile,
		FromDate: opts.FromDate,
		ToDate:   opts.ToDate,
		Context:  opts.Context,
	})
}

func splitLines(s string) []string {
	if s == "" {
		return nil
	}
	lines := strings.SplitAfter(s, "\n")
	last := len(lines) - 1
	if lines[last] == "" {
		lines = lines[:last]
	} else if !strings.HasSuffix(lines[last], "\n") {
		lines[last] += "\n"
	}
	return lines
}

func WriteUnified(w io.Writer, from, to string, opts Options) error {
	s, err := Unified(from, to, opts)
	if err != nil {
		return err
	}
	_, err = io.WriteString(w, s)
	return err
}

func Equal(a, b string) bool {
	return a == b
}

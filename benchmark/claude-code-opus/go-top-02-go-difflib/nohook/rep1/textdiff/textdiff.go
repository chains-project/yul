// Package textdiff computes and renders unified diffs between two texts.
package textdiff

import (
	"strings"

	udiff "github.com/aymanbagabas/go-udiff"
)

// DefaultContext is the number of unchanged lines shown around each change.
const DefaultContext = udiff.DefaultContextLines

// Options controls how a diff is rendered.
type Options struct {
	OldLabel string // header label for the old text (default "old")
	NewLabel string // header label for the new text (default "new")
	Context  int    // context lines; negative means DefaultContext
	Color    bool   // emit ANSI colors for terminal display
}

// Unified returns a unified diff from oldText to newText using default
// options. It returns "" when the texts are identical.
func Unified(oldText, newText string) string {
	return UnifiedWith(oldText, newText, Options{Context: -1})
}

// UnifiedWith returns a unified diff from oldText to newText rendered
// according to opts. It returns "" when the texts are identical.
func UnifiedWith(oldText, newText string, opts Options) string {
	if oldText == newText {
		return ""
	}
	if opts.OldLabel == "" {
		opts.OldLabel = "old"
	}
	if opts.NewLabel == "" {
		opts.NewLabel = "new"
	}
	if opts.Context < 0 {
		opts.Context = DefaultContext
	}

	edits := udiff.Lines(oldText, newText)
	out, err := udiff.ToUnified(opts.OldLabel, opts.NewLabel, oldText, edits, opts.Context)
	if err != nil {
		// Edits produced by udiff.Lines are always valid for oldText.
		panic("textdiff: " + err.Error())
	}
	if opts.Color {
		out = colorize(out)
	}
	return out
}

const (
	ansiReset = "\x1b[0m"
	ansiBold  = "\x1b[1m"
	ansiRed   = "\x1b[31m"
	ansiGreen = "\x1b[32m"
	ansiCyan  = "\x1b[36m"
)

func colorize(diff string) string {
	var b strings.Builder
	for _, line := range strings.SplitAfter(diff, "\n") {
		if line == "" {
			continue
		}
		body, nl := strings.CutSuffix(line, "\n")
		var color string
		switch {
		case strings.HasPrefix(body, "---"), strings.HasPrefix(body, "+++"):
			color = ansiBold
		case strings.HasPrefix(body, "@@"):
			color = ansiCyan
		case strings.HasPrefix(body, "-"):
			color = ansiRed
		case strings.HasPrefix(body, "+"):
			color = ansiGreen
		}
		if color != "" {
			b.WriteString(color + body + ansiReset)
		} else {
			b.WriteString(body)
		}
		if nl {
			b.WriteByte('\n')
		}
	}
	return b.String()
}

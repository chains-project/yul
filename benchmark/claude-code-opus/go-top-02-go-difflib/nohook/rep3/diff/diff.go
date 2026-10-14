// Package diff computes and renders line-oriented unified diffs.
package diff

import (
	"strings"

	udiff "github.com/aymanbagabas/go-udiff"
)

// DefaultContext is the number of unchanged lines shown around each change.
const DefaultContext = udiff.DefaultContextLines

// Unified returns a unified diff that turns old into new, using the given
// labels in the "---"/"+++" header lines. It returns "" when the inputs are
// equal. A negative context uses DefaultContext.
func Unified(oldLabel, newLabel, old, new string, context int) string {
	if old == new {
		return ""
	}
	if context < 0 {
		context = DefaultContext
	}
	edits := udiff.Lines(old, new)
	out, err := udiff.ToUnified(oldLabel, newLabel, old, edits, context)
	if err != nil {
		// Edits produced by udiff.Lines are always valid for old.
		panic("diff: " + err.Error())
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

// Colorize adds ANSI terminal colors to a unified diff produced by Unified.
func Colorize(unified string) string {
	if unified == "" {
		return ""
	}
	var b strings.Builder
	for _, line := range strings.SplitAfter(unified, "\n") {
		if line == "" {
			continue
		}
		body := strings.TrimSuffix(line, "\n")
		nl := line[len(body):]
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
		if color == "" {
			b.WriteString(line)
			continue
		}
		b.WriteString(color + body + ansiReset + nl)
	}
	return b.String()
}

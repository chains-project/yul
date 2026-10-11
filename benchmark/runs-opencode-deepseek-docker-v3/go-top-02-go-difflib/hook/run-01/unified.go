// Package difftool computes and renders unified diffs between two texts.
//
// The implementation depends only on the standard library. Diffs are computed
// with a longest-common-subsequence backtrack and grouped into hunks using the
// usual three lines of surrounding context.
package difftool

import (
	"fmt"
	"io"
	"strings"
)

// DefaultContext is the number of unchanged lines shown around each change.
const DefaultContext = 3

// Options controls how a unified diff is rendered.
type Options struct {
	// FromName and ToName label the --- and +++ header lines. They default to
	// "a" and "b" when empty.
	FromName string
	ToName   string
	// Context is the number of unchanged lines to show around each change.
	// Values <= 0 fall back to DefaultContext.
	Context int
}

func (o Options) context() int {
	if o.Context <= 0 {
		return DefaultContext
	}
	return o.Context
}

// opCode describes one contiguous edit: an equal, delete, insert or replace
// region, using zero-based half-open ranges [i1,i2) in a and [j1,j2) in b.
type opCode struct {
	tag    byte // 'e', 'd', 'i' or 'r'
	i1, i2 int
	j1, j2 int
}

// SplitLines splits text into lines. A single trailing newline is treated as a
// line terminator rather than introducing an extra empty line.
func SplitLines(text string) []string {
	if text == "" {
		return nil
	}
	text = strings.TrimSuffix(text, "\n")
	return strings.Split(text, "\n")
}

// Unified builds a unified diff of a and b and returns it as a string. It
// returns the empty string when the inputs are identical.
func Unified(a, b []string, opts Options) string {
	var sb strings.Builder
	_ = WriteUnified(&sb, a, b, opts)
	return sb.String()
}

// UnifiedText is like Unified but accepts the inputs as strings.
func UnifiedText(a, b string, opts Options) string {
	return Unified(SplitLines(a), SplitLines(b), opts)
}

// WriteUnified writes a unified diff of a and b to w. Nothing is written when
// the inputs are identical.
func WriteUnified(w io.Writer, a, b []string, opts Options) error {
	groups := groupOpCodes(lineOpCodes(a, b), opts.context())
	if len(groups) == 0 {
		return nil
	}

	fromName, toName := opts.FromName, opts.ToName
	if fromName == "" {
		fromName = "a"
	}
	if toName == "" {
		toName = "b"
	}

	var sb strings.Builder
	fmt.Fprintf(&sb, "--- %s\n+++ %s\n", fromName, toName)
	for _, g := range groups {
		first, last := g[0], g[len(g)-1]
		fmt.Fprintf(&sb, "@@ -%s +%s @@\n", formatRange(first.i1, last.i2), formatRange(first.j1, last.j2))
		for _, c := range g {
			switch c.tag {
			case 'e':
				writePrefixed(&sb, ' ', a[c.i1:c.i2])
			case 'd':
				writePrefixed(&sb, '-', a[c.i1:c.i2])
			case 'i':
				writePrefixed(&sb, '+', b[c.j1:c.j2])
			case 'r':
				writePrefixed(&sb, '-', a[c.i1:c.i2])
				writePrefixed(&sb, '+', b[c.j1:c.j2])
			}
		}
	}

	_, err := io.WriteString(w, sb.String())
	return err
}

func writePrefixed(sb *strings.Builder, prefix byte, lines []string) {
	for _, line := range lines {
		sb.WriteByte(prefix)
		sb.WriteString(line)
		sb.WriteByte('\n')
	}
}

// formatRange renders a half-open [start,end) range in unified-diff syntax.
// A single line is written as just its number, an empty range as "n,0".
func formatRange(start, end int) string {
	switch count := end - start; {
	case count == 0:
		return fmt.Sprintf("%d,0", start)
	case count == 1:
		return fmt.Sprintf("%d", start+1)
	default:
		return fmt.Sprintf("%d,%d", start+1, count)
	}
}

// lineOpCodes computes the edit script between a and b using an LCS table.
func lineOpCodes(a, b []string) []opCode {
	m, n := len(a), len(b)

	// lcs[i][j] is the LCS length of a[i:] and b[j:].
	lcs := make([][]int, m+1)
	for i := range lcs {
		lcs[i] = make([]int, n+1)
	}
	for i := m - 1; i >= 0; i-- {
		for j := n - 1; j >= 0; j-- {
			switch {
			case a[i] == b[j]:
				lcs[i][j] = lcs[i+1][j+1] + 1
			case lcs[i+1][j] >= lcs[i][j+1]:
				lcs[i][j] = lcs[i+1][j]
			default:
				lcs[i][j] = lcs[i][j+1]
			}
		}
	}

	var ops []opCode
	i, j := 0, 0
	for i < m && j < n {
		switch {
		case a[i] == b[j]:
			ops = append(ops, opCode{'e', i, i + 1, j, j + 1})
			i++
			j++
		case lcs[i+1][j] >= lcs[i][j+1]:
			ops = append(ops, opCode{'d', i, i + 1, j, j})
			i++
		default:
			ops = append(ops, opCode{'i', i, i, j, j + 1})
			j++
		}
	}
	for ; i < m; i++ {
		ops = append(ops, opCode{'d', i, i + 1, j, j})
	}
	for ; j < n; j++ {
		ops = append(ops, opCode{'i', i, i, j, j + 1})
	}
	return coalesce(ops)
}

// coalesce merges adjacent opcodes of the same kind, and folds a delete
// immediately followed by an insert into a single replace.
func coalesce(ops []opCode) []opCode {
	out := make([]opCode, 0, len(ops))
	for _, c := range ops {
		if len(out) == 0 {
			out = append(out, c)
			continue
		}
		last := &out[len(out)-1]
		switch {
		case last.tag == c.tag && last.i2 == c.i1 && last.j2 == c.j1:
			last.i2 = c.i2
			last.j2 = c.j2
		case last.tag == 'd' && c.tag == 'i' && last.i2 == c.i1 && last.j2 == c.j1:
			last.tag = 'r'
			last.i2 = c.i2
			last.j2 = c.j2
		default:
			out = append(out, c)
		}
	}
	return out
}

// groupOpCodes splits the edit script into hunks that include at most n lines
// of context around each change. Runs of unchanged lines longer than 2n are
// shortened so they cannot be split awkwardly, and hunks closer than 2n lines
// apart are merged.
func groupOpCodes(codes []opCode, n int) [][]opCode {
	if len(codes) == 0 {
		return nil
	}
	codes = append([]opCode(nil), codes...)

	if codes[0].tag == 'e' {
		c := codes[0]
		codes[0] = opCode{'e', max(c.i1, c.i2-n), c.i2, max(c.j1, c.j2-n), c.j2}
	}
	if last := len(codes) - 1; codes[last].tag == 'e' {
		c := codes[last]
		codes[last] = opCode{'e', c.i1, min(c.i2, c.i1+n), c.j1, min(c.j2, c.j1+n)}
	}

	nn := 2 * n
	var groups [][]opCode
	var current []opCode
	for _, c := range codes {
		if c.tag == 'e' && c.i2-c.i1 > nn {
			current = append(current, opCode{'e', c.i1, min(c.i2, c.i1+n), c.j1, min(c.j2, c.j1+n)})
			groups = append(groups, current)
			current = nil
			c.i1 = max(c.i1, c.i2-n)
			c.j1 = max(c.j1, c.j2-n)
		}
		current = append(current, c)
	}
	if len(current) > 0 && !(len(current) == 1 && current[0].tag == 'e') {
		groups = append(groups, current)
	}
	return groups
}

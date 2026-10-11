// Package unidiff computes and renders unified diffs between two pieces of
// text. It is intended for use in tests and developer tooling that needs to
// display readable differences.
package unidiff

import (
	"fmt"
	"strings"
)

// DefaultContext is the number of unchanged lines shown around each change.
const DefaultContext = 3

type lineKind int

const (
	equal lineKind = iota
	delete
	insert
)

// op is a single edit-script element: one line of input classified as equal,
// deleted from the old text, or inserted into the new text.
type op struct {
	kind lineKind
	text string
}

// Unified returns the unified diff between a and b, using DefaultContext
// lines of surrounding context. An empty string is returned when the texts are
// identical.
func Unified(a, b string) string {
	return UnifiedContext(a, b, DefaultContext)
}

// UnifiedContext is like Unified but lets the caller choose how many lines of
// unchanged context are shown around each change. A negative context is
// treated as zero.
func UnifiedContext(a, b string, context int) string {
	if context < 0 {
		context = 0
	}
	if a == b {
		return ""
	}

	ops := diff(splitLines(a), splitLines(b))
	return format(ops, context)
}

// splitLines splits s into lines suitable for diffing. A trailing newline does
// not produce a final empty line. An empty string produces no lines.
func splitLines(s string) []string {
	if s == "" {
		return nil
	}
	s = strings.TrimSuffix(s, "\n")
	return strings.Split(s, "\n")
}

// diff builds an edit script from a to b using a longest-common-subsequence
// table followed by a backtrack.
func diff(a, b []string) []op {
	n, m := len(a), len(b)
	lcs := make([][]int, n+1)
	for i := range lcs {
		lcs[i] = make([]int, m+1)
	}
	for i := n - 1; i >= 0; i-- {
		for j := m - 1; j >= 0; j-- {
			if a[i] == b[j] {
				lcs[i][j] = lcs[i+1][j+1] + 1
			} else if lcs[i+1][j] >= lcs[i][j+1] {
				lcs[i][j] = lcs[i+1][j]
			} else {
				lcs[i][j] = lcs[i][j+1]
			}
		}
	}

	ops := make([]op, 0, n+m)
	i, j := 0, 0
	for i < n && j < m {
		switch {
		case a[i] == b[j]:
			ops = append(ops, op{equal, a[i]})
			i++
			j++
		case lcs[i+1][j] >= lcs[i][j+1]:
			ops = append(ops, op{delete, a[i]})
			i++
		default:
			ops = append(ops, op{insert, b[j]})
			j++
		}
	}
	for ; i < n; i++ {
		ops = append(ops, op{delete, a[i]})
	}
	for ; j < m; j++ {
		ops = append(ops, op{insert, b[j]})
	}
	return ops
}

// format renders an edit script as a unified diff with the given context.
func format(ops []op, context int) string {
	var changes []int
	for i, o := range ops {
		if o.kind != equal {
			changes = append(changes, i)
		}
	}
	if len(changes) == 0 {
		return ""
	}

	var b strings.Builder
	b.WriteString("--- a\n+++ b\n")

	for ci := 0; ci < len(changes); {
		start := changes[ci]
		end := start
		ci++
		for ci < len(changes) && changes[ci]-end-1 <= 2*context {
			end = changes[ci]
			ci++
		}

		hunkStart := max(0, start-context)
		hunkEnd := min(len(ops)-1, end+context)

		writeHunk(&b, ops, hunkStart, hunkEnd)
	}
	return b.String()
}

// writeHunk renders a single @@ hunk covering ops[lo:hi+1].
func writeHunk(b *strings.Builder, ops []op, lo, hi int) {
	aStart, bStart := 1, 1
	for i := 0; i < lo; i++ {
		switch ops[i].kind {
		case equal:
			aStart++
			bStart++
		case delete:
			aStart++
		case insert:
			bStart++
		}
	}

	aCount, bCount := 0, 0
	for i := lo; i <= hi; i++ {
		switch ops[i].kind {
		case equal:
			aCount++
			bCount++
		case delete:
			aCount++
		case insert:
			bCount++
		}
	}

	fmt.Fprintf(b, "@@ -%s +%s @@\n", formatRange(aStart, aCount), formatRange(bStart, bCount))
	for i := lo; i <= hi; i++ {
		switch ops[i].kind {
		case equal:
			b.WriteString(" " + ops[i].text + "\n")
		case delete:
			b.WriteString("-" + ops[i].text + "\n")
		case insert:
			b.WriteString("+" + ops[i].text + "\n")
		}
	}
}

// formatRange renders a unified-diff line range. A single-line range omits the
// count, matching the output of GNU diff.
func formatRange(start, count int) string {
	if count == 1 {
		return fmt.Sprintf("%d", start)
	}
	return fmt.Sprintf("%d,%d", start, count)
}

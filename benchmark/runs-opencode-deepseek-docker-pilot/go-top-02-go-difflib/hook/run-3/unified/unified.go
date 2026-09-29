// Package unified computes and formats unified diffs between two pieces of
// text. It has no dependencies outside the standard library, which makes it
// convenient to use from tests.
package unified

import (
	"fmt"
	"strconv"
	"strings"
)

// DefaultContext is the number of unchanged lines shown around each change,
// matching the default used by diff(1).
const DefaultContext = 3

type op int

const (
	opEqual op = iota
	opDelete
	opInsert
)

type edit struct {
	op   op
	line string
}

// Diff returns a unified diff between old and new using DefaultContext lines
// of context. The output includes "--- old" and "+++ new" headers. It returns
// an empty string when the inputs are identical.
func Diff(old, new string) string {
	return DiffContext(old, new, DefaultContext)
}

// DiffContext is like Diff but controls how many lines of surrounding context
// are included with each change.
func DiffContext(old, new string, context int) string {
	return DiffNamed(old, new, "old", "new", context)
}

// DiffNamed is like DiffContext but uses the supplied labels for the "---" and
// "+++" header lines.
func DiffNamed(old, new, oldLabel, newLabel string, context int) string {
	if context < 0 {
		context = 0
	}
	edits := diffLines(splitLines(old), splitLines(new))
	hunks := buildHunks(edits, context)
	if len(hunks) == 0 {
		return ""
	}
	var b strings.Builder
	fmt.Fprintf(&b, "--- %s\n+++ %s\n", oldLabel, newLabel)
	for _, h := range hunks {
		fmt.Fprintf(&b, "@@ -%s +%s @@\n", formatRange(h.oldStart, h.oldCount), formatRange(h.newStart, h.newCount))
		for _, e := range h.edits {
			writeEdit(&b, e)
		}
	}
	return b.String()
}

type hunk struct {
	edits              []edit
	oldStart, oldCount int
	newStart, newCount int
}

// splitLines splits s into lines while preserving each line's trailing
// newline. The final line has no newline when s does not end with one.
func splitLines(s string) []string {
	if s == "" {
		return nil
	}
	lines := strings.SplitAfter(s, "\n")
	if lines[len(lines)-1] == "" {
		lines = lines[:len(lines)-1]
	}
	return lines
}

// diffLines computes an edit script turning a into b using a longest common
// subsequence.
func diffLines(a, b []string) []edit {
	n, m := len(a), len(b)
	if n == 0 && m == 0 {
		return nil
	}

	// dp[i][j] is the length of the LCS of a[i:] and b[j:].
	dp := make([][]int, n+1)
	for i := range dp {
		dp[i] = make([]int, m+1)
	}
	for i := n - 1; i >= 0; i-- {
		for j := m - 1; j >= 0; j-- {
			switch {
			case a[i] == b[j]:
				dp[i][j] = dp[i+1][j+1] + 1
			case dp[i+1][j] >= dp[i][j+1]:
				dp[i][j] = dp[i+1][j]
			default:
				dp[i][j] = dp[i][j+1]
			}
		}
	}

	var edits []edit
	for i, j := 0, 0; i < n || j < m; {
		switch {
		case i < n && j < m && a[i] == b[j]:
			edits = append(edits, edit{opEqual, a[i]})
			i++
			j++
		case i < n && (j == m || dp[i+1][j] >= dp[i][j+1]):
			edits = append(edits, edit{opDelete, a[i]})
			i++
		default:
			edits = append(edits, edit{opInsert, b[j]})
			j++
		}
	}
	return normalize(edits)
}

// normalize reorders each run of changes so deletions precede insertions, the
// conventional ordering used by unified diff.
func normalize(edits []edit) []edit {
	out := make([]edit, 0, len(edits))
	for i := 0; i < len(edits); {
		if edits[i].op == opEqual {
			out = append(out, edits[i])
			i++
			continue
		}
		j := i
		var deletes, inserts []edit
		for j < len(edits) && edits[j].op != opEqual {
			if edits[j].op == opDelete {
				deletes = append(deletes, edits[j])
			} else {
				inserts = append(inserts, edits[j])
			}
			j++
		}
		out = append(out, deletes...)
		out = append(out, inserts...)
		i = j
	}
	return out
}

// buildHunks groups changes into hunks separated by more than 2*context lines
// of unchanged text and computes their line ranges.
func buildHunks(edits []edit, context int) []hunk {
	var changes []int
	for i, e := range edits {
		if e.op != opEqual {
			changes = append(changes, i)
		}
	}
	if len(changes) == 0 {
		return nil
	}

	// Prefix counts of old and new lines consumed before each edit index.
	oldPrefix := make([]int, len(edits)+1)
	newPrefix := make([]int, len(edits)+1)
	for i, e := range edits {
		oldPrefix[i+1] = oldPrefix[i]
		newPrefix[i+1] = newPrefix[i]
		if e.op != opInsert {
			oldPrefix[i+1]++
		}
		if e.op != opDelete {
			newPrefix[i+1]++
		}
	}

	var hunks []hunk
	groupStart := changes[0]
	flush := func(last int) {
		s := groupStart - context
		if s < 0 {
			s = 0
		}
		e := last + context + 1
		if e > len(edits) {
			e = len(edits)
		}
		h := hunk{edits: edits[s:e]}
		h.oldCount = oldPrefix[e] - oldPrefix[s]
		h.newCount = newPrefix[e] - newPrefix[s]
		h.oldStart = oldPrefix[s] + 1
		if h.oldCount == 0 {
			h.oldStart = oldPrefix[s]
		}
		h.newStart = newPrefix[s] + 1
		if h.newCount == 0 {
			h.newStart = newPrefix[s]
		}
		hunks = append(hunks, h)
	}
	prev := changes[0]
	for _, c := range changes[1:] {
		if c-prev-1 <= 2*context {
			prev = c
			continue
		}
		flush(prev)
		groupStart = c
		prev = c
	}
	flush(prev)
	return hunks
}

func writeEdit(b *strings.Builder, e edit) {
	switch e.op {
	case opEqual:
		b.WriteByte(' ')
	case opDelete:
		b.WriteByte('-')
	case opInsert:
		b.WriteByte('+')
	}
	b.WriteString(e.line)
	if !strings.HasSuffix(e.line, "\n") {
		b.WriteString("\n\\ No newline at end of file\n")
	}
}

func formatRange(start, count int) string {
	if count == 1 {
		return strconv.Itoa(start)
	}
	return strconv.Itoa(start) + "," + strconv.Itoa(count)
}

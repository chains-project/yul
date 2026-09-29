// Package diff computes unified diffs between two pieces of text.
//
// It implements the Myers O(ND) difference algorithm and renders the result in
// the same format produced by `diff -u`, which is useful when a testing tool
// needs to show why two strings differ.
package diff

import (
	"fmt"
	"strings"
)

// Op describes what happens to a single line when transforming the old text
// into the new text.
type Op int

const (
	// Equal marks a line present in both texts.
	Equal Op = iota
	// Delete marks a line present only in the old text.
	Delete
	// Insert marks a line present only in the new text.
	Insert
)

// Edit is a single line-level operation.
type Edit struct {
	Op   Op
	Text string
}

// DefaultContext is the number of unchanged lines shown around each change.
const DefaultContext = 3

// Myers computes the sequence of line edits that turns a into b using the
// Myers O(ND) difference algorithm. The returned edits are in order.
func Myers(a, b []string) []Edit {
	n, m := len(a), len(b)
	if n == 0 && m == 0 {
		return nil
	}

	maxD := n + m
	offset := maxD
	v := make([]int, 2*maxD+1)
	trace := make([][]int, 0, maxD+1)

	found := false
	for d := 0; d <= maxD && !found; d++ {
		snapshot := make([]int, len(v))
		copy(snapshot, v)
		trace = append(trace, snapshot)

		for k := -d; k <= d; k += 2 {
			var x int
			if k == -d || (k != d && v[offset+k-1] < v[offset+k+1]) {
				x = v[offset+k+1]
			} else {
				x = v[offset+k-1] + 1
			}
			y := x - k
			for x < n && y < m && a[x] == b[y] {
				x++
				y++
			}
			v[offset+k] = x
			if x >= n && y >= m {
				found = true
				break
			}
		}
	}

	return backtrack(trace, offset, a, b)
}

func backtrack(trace [][]int, offset int, a, b []string) []Edit {
	x, y := len(a), len(b)
	edits := make([]Edit, 0, x+y)

	for d := len(trace) - 1; d >= 0; d-- {
		v := trace[d]
		k := x - y

		var prevK int
		if k == -d || (k != d && v[offset+k-1] < v[offset+k+1]) {
			prevK = k + 1
		} else {
			prevK = k - 1
		}
		prevX := v[offset+prevK]
		prevY := prevX - prevK

		for x > prevX && y > prevY {
			edits = append(edits, Edit{Op: Equal, Text: a[x-1]})
			x--
			y--
		}

		if d > 0 {
			if x == prevX {
				edits = append(edits, Edit{Op: Insert, Text: b[y-1]})
				y--
			} else {
				edits = append(edits, Edit{Op: Delete, Text: a[x-1]})
				x--
			}
		}
	}

	for i, j := 0, len(edits)-1; i < j; i, j = i+1, j-1 {
		edits[i], edits[j] = edits[j], edits[i]
	}
	return edits
}

// Unified returns a unified diff between a and b using DefaultContext lines of
// context. It returns an empty string when the texts are identical.
func Unified(a, b string) string {
	return UnifiedContext(a, b, DefaultContext)
}

// UnifiedContext is like Unified but with a caller-supplied number of context
// lines. A negative context is treated as zero.
func UnifiedContext(a, b string, context int) string {
	return UnifiedLabels(a, b, "a", "b", context)
}

// UnifiedLabels is like UnifiedContext but lets the caller choose the labels
// written after the leading "---" and "+++". An empty label omits that header
// line. It returns an empty string when the texts are identical.
func UnifiedLabels(a, b, oldLabel, newLabel string, context int) string {
	if context < 0 {
		context = 0
	}

	aLines, aNewline := splitLines(a)
	bLines, bNewline := splitLines(b)

	edits := Myers(aLines, bLines)
	if !hasChange(edits) {
		return ""
	}

	var body strings.Builder
	for _, g := range hunks(edits, context) {
		writeHunk(&body, edits, g[0], g[1], context, aLines, aNewline, bLines, bNewline)
	}

	if body.Len() == 0 {
		return ""
	}

	var out strings.Builder
	if oldLabel != "" {
		out.WriteString("--- " + oldLabel + "\n")
	}
	if newLabel != "" {
		out.WriteString("+++ " + newLabel + "\n")
	}
	out.WriteString(body.String())
	return out.String()
}

func splitLines(s string) ([]string, bool) {
	if s == "" {
		return nil, true
	}
	hasTrailing := strings.HasSuffix(s, "\n")
	lines := strings.Split(s, "\n")
	if hasTrailing {
		lines = lines[:len(lines)-1]
	}
	return lines, hasTrailing
}

func hasChange(edits []Edit) bool {
	for _, e := range edits {
		if e.Op != Equal {
			return true
		}
	}
	return false
}

// hunks groups the indices of changed edits into inclusive [start,end) ranges,
// merging changes that are no further apart than twice the context.
func hunks(edits []Edit, context int) [][2]int {
	var changes []int
	for i, e := range edits {
		if e.Op != Equal {
			changes = append(changes, i)
		}
	}
	if len(changes) == 0 {
		return nil
	}

	var groups [][2]int
	start, last := changes[0], changes[0]
	for _, c := range changes[1:] {
		if c-last-1 <= 2*context {
			last = c
			continue
		}
		groups = append(groups, [2]int{start, last + 1})
		start, last = c, c
	}
	groups = append(groups, [2]int{start, last + 1})
	return groups
}

func writeHunk(
	out *strings.Builder,
	edits []Edit,
	first, last, context int,
	aLines []string,
	aNewline bool,
	bLines []string,
	bNewline bool,
) {
	start := first - context
	if start < 0 {
		start = 0
	}
	end := last + context
	if end > len(edits) {
		end = len(edits)
	}

	oldStart, newStart := 1, 1
	for i := 0; i < start; i++ {
		switch edits[i].Op {
		case Equal:
			oldStart++
			newStart++
		case Delete:
			oldStart++
		case Insert:
			newStart++
		}
	}

	var oldCount, newCount int
	for i := start; i < end; i++ {
		switch edits[i].Op {
		case Equal:
			oldCount++
			newCount++
		case Delete:
			oldCount++
		case Insert:
			newCount++
		}
	}
	if oldCount == 0 {
		oldStart--
	}
	if newCount == 0 {
		newStart--
	}

	out.WriteString("@@ " + rangePart("-", oldStart, oldCount) + " " + rangePart("+", newStart, newCount) + " @@\n")

	for i := start; i < end; i++ {
		e := edits[i]
		var prefix string
		switch e.Op {
		case Equal:
			prefix = " "
		case Delete:
			prefix = "-"
		case Insert:
			prefix = "+"
		}
		out.WriteString(prefix + e.Text + "\n")

		if !hasNewline(e, i, edits, aLines, aNewline, bLines, bNewline) {
			out.WriteString("\\ No newline at end of file\n")
		}
	}
}

func hasNewline(
	e Edit,
	index int,
	edits []Edit,
	aLines []string,
	aNewline bool,
	bLines []string,
	bNewline bool,
) bool {
	oldIdx, newIdx := 0, 0
	for i := 0; i <= index; i++ {
		switch edits[i].Op {
		case Equal:
			oldIdx++
			newIdx++
		case Delete:
			oldIdx++
		case Insert:
			newIdx++
		}
	}

	oldMissing := (e.Op == Equal || e.Op == Delete) && oldIdx == len(aLines) && !aNewline
	newMissing := (e.Op == Equal || e.Op == Insert) && newIdx == len(bLines) && !bNewline
	return !(oldMissing || newMissing)
}

func rangePart(sign string, start, count int) string {
	if count == 1 {
		return fmt.Sprintf("%s%d", sign, start)
	}
	return fmt.Sprintf("%s%d,%d", sign, start, count)
}

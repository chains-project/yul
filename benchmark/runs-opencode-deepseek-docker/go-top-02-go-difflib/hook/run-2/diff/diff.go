// Package diff computes and renders unified diffs between two pieces of text.
//
// It is self-contained and depends only on the standard library, which makes
// it convenient to use from tests and command-line tools alike.
package diff

import (
	"fmt"
	"strconv"
	"strings"
)

// DefaultContext is the number of unchanged lines shown around each change by
// Unified.
const DefaultContext = 3

// Options configures the output produced by UnifiedWith.
type Options struct {
	// FromFile and ToFile label the two sides in the "---" and "+++" header
	// lines. They default to "old" and "new" when left empty.
	FromFile string
	ToFile   string

	// Context is the number of unchanged lines displayed around each change.
	// Negative values are treated as zero.
	Context int
}

// Unified returns a unified diff between oldText and newText, using
// DefaultContext lines of context and the labels "old" and "new". It returns
// the empty string when the two texts are identical.
func Unified(oldText, newText string) string {
	return UnifiedWith(oldText, newText, Options{Context: DefaultContext})
}

// UnifiedWith returns a unified diff between oldText and newText. It returns
// the empty string when the two texts are identical.
func UnifiedWith(oldText, newText string, opts Options) string {
	from, to := opts.FromFile, opts.ToFile
	if from == "" {
		from = "old"
	}
	if to == "" {
		to = "new"
	}
	context := opts.Context
	if context < 0 {
		context = 0
	}

	oldLines := splitLines(oldText)
	newLines := splitLines(newText)
	edits := myers(oldLines, newLines)
	hunks := groupHunks(edits, context)
	if len(hunks) == 0 {
		return ""
	}

	var b strings.Builder
	fmt.Fprintf(&b, "--- %s\n+++ %s\n", from, to)
	for _, h := range hunks {
		writeHunk(&b, edits, h)
	}
	return b.String()
}

// line is a single line of text together with whether it was terminated by a
// newline in the source text.
type line struct {
	text       string
	hasNewline bool
}

// splitLines splits text into lines, discarding the newline terminators but
// remembering for each line whether one was present.
func splitLines(text string) []line {
	if text == "" {
		return nil
	}
	parts := strings.Split(text, "\n")
	lines := make([]line, 0, len(parts))
	for i, part := range parts {
		if i == len(parts)-1 {
			if part == "" && strings.HasSuffix(text, "\n") {
				break
			}
			lines = append(lines, line{text: part})
			break
		}
		lines = append(lines, line{text: part, hasNewline: true})
	}
	return lines
}

type opKind uint8

const (
	opEqual opKind = iota
	opDelete
	opInsert
)

// edit is a single step of an edit script. The line comes from the old text
// for opEqual/opDelete and from the new text for opInsert.
type edit struct {
	kind opKind
	line line
}

// myers computes a shortest edit script between a and b using Myers' O(ND)
// difference algorithm.
func myers(a, b []line) []edit {
	n, m := len(a), len(b)
	max := n + m
	if max == 0 {
		return nil
	}

	offset := max
	v := make([]int, 2*max+1)
	trace := make([][]int, 0, max+1)

	finalD := 0
found:
	for d := 0; d <= max; d++ {
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
			for x < n && y < m && a[x].text == b[y].text && a[x].hasNewline == b[y].hasNewline {
				x++
				y++
			}
			v[offset+k] = x
			if x >= n && y >= m {
				finalD = d
				break found
			}
		}
	}

	return compact(backtrack(trace, a, b, offset, finalD))
}

// compact slides change blocks across neighbouring unchanged lines in order to
// merge changes that Myers' algorithm would otherwise scatter across runs of
// repeated lines. For example, replacing the first of many identical lines can
// otherwise surface as an insertion at the top and a deletion at the bottom.
//
// A block may cross a run of unchanged lines only when every changed line and
// every crossed line have the same content, which keeps each individual move
// valid. Every successful move merges two blocks, so the loop terminates. The
// order of the deletes and inserts within each block is then normalised.
func compact(edits []edit) []edit {
	for {
		n := len(edits)
		merged := false

		for i := 0; i < n && !merged; {
			if edits[i].kind == opEqual {
				i++
				continue
			}

			blockStart := i
			for i < n && edits[i].kind != opEqual {
				i++
			}
			blockEnd := i
			gapStart := i
			for i < n && edits[i].kind == opEqual {
				i++
			}
			gapEnd := i
			if gapEnd >= n {
				break
			}

			rightStart := gapEnd
			rightEnd := rightStart
			for rightEnd < n && edits[rightEnd].kind != opEqual {
				rightEnd++
			}

			switch {
			case canCross(edits[gapStart:gapEnd], edits[rightStart:rightEnd]):
				rotate(edits, blockEnd, rightStart, rightEnd)
				merged = true
			case canCross(edits[gapStart:gapEnd], edits[blockStart:blockEnd]):
				rotate(edits, blockStart, blockEnd, gapEnd)
				merged = true
			}
		}

		if !merged {
			return normalizeOrder(edits)
		}
	}
}

// canCross reports whether block can be shifted across gap one edit at a time,
// which requires every line in both the gap and the block to be identical.
func canCross(gap, block []edit) bool {
	if len(gap) == 0 || len(block) == 0 {
		return false
	}
	want := block[0].line
	for _, e := range block {
		if e.line != want {
			return false
		}
	}
	for _, e := range gap {
		if e.line != want {
			return false
		}
	}
	return true
}

// normalizeOrder rewrites each run of changes so that deletions precede
// insertions, matching the conventional layout of a unified diff. Deletions
// only consume old lines and insertions only produce new lines, so reordering
// them within a single replacement region cannot change the result.
func normalizeOrder(edits []edit) []edit {
	out := make([]edit, 0, len(edits))
	for i := 0; i < len(edits); {
		if edits[i].kind == opEqual {
			out = append(out, edits[i])
			i++
			continue
		}
		j := i
		for j < len(edits) && edits[j].kind != opEqual {
			j++
		}
		for _, e := range edits[i:j] {
			if e.kind == opDelete {
				out = append(out, e)
			}
		}
		for _, e := range edits[i:j] {
			if e.kind == opInsert {
				out = append(out, e)
			}
		}
		i = j
	}
	return out
}

// rotate rearranges edits[lo:hi] from [lo:mid), [mid:hi) to [mid:hi), [lo:mid).
func rotate(edits []edit, lo, mid, hi int) {
	reverseEdits(edits[lo:mid])
	reverseEdits(edits[mid:hi])
	reverseEdits(edits[lo:hi])
}

func reverseEdits(edits []edit) {
	for i, j := 0, len(edits)-1; i < j; i, j = i+1, j-1 {
		edits[i], edits[j] = edits[j], edits[i]
	}
}

// backtrack walks the trace produced by myers and returns the edit script in
// forward order.
func backtrack(trace [][]int, a, b []line, offset, finalD int) []edit {
	x, y := len(a), len(b)
	edits := make([]edit, 0, x+y)

	for d := finalD; d >= 0; d-- {
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
			edits = append(edits, edit{kind: opEqual, line: a[x-1]})
			x--
			y--
		}
		if d > 0 {
			if x == prevX {
				edits = append(edits, edit{kind: opInsert, line: b[prevY]})
			} else {
				edits = append(edits, edit{kind: opDelete, line: a[prevX]})
			}
		}
		x, y = prevX, prevY
	}

	for i, j := 0, len(edits)-1; i < j; i, j = i+1, j-1 {
		edits[i], edits[j] = edits[j], edits[i]
	}
	return edits
}

// hunk is the half-open range [start, end) of edits that make up one hunk.
type hunk struct {
	start int
	end   int
}

// groupHunks collects the changes in edits into hunks, each padded with up to
// context unchanged lines and merging hunks whose context regions touch.
func groupHunks(edits []edit, context int) []hunk {
	var changed []int
	for i, e := range edits {
		if e.kind != opEqual {
			changed = append(changed, i)
		}
	}
	if len(changed) == 0 {
		return nil
	}

	clamp := func(i int) int {
		if i < 0 {
			return 0
		}
		if i > len(edits) {
			return len(edits)
		}
		return i
	}

	current := hunk{start: clamp(changed[0] - context), end: clamp(changed[0] + context + 1)}
	var hunks []hunk
	for _, c := range changed[1:] {
		if c-context <= current.end {
			if end := clamp(c + context + 1); end > current.end {
				current.end = end
			}
			continue
		}
		hunks = append(hunks, current)
		current = hunk{start: clamp(c - context), end: clamp(c + context + 1)}
	}
	return append(hunks, current)
}

// writeHunk renders a single hunk, including its "@@" header, to b.
func writeHunk(b *strings.Builder, edits []edit, h hunk) {
	oldStart, newStart := 1, 1
	for i := 0; i < h.start; i++ {
		switch edits[i].kind {
		case opEqual:
			oldStart++
			newStart++
		case opDelete:
			oldStart++
		case opInsert:
			newStart++
		}
	}

	oldCount, newCount := 0, 0
	for i := h.start; i < h.end; i++ {
		switch edits[i].kind {
		case opEqual:
			oldCount++
			newCount++
		case opDelete:
			oldCount++
		case opInsert:
			newCount++
		}
	}

	fmt.Fprintf(b, "@@ -%s +%s @@\n", formatRange(oldStart, oldCount), formatRange(newStart, newCount))

	for i := h.start; i < h.end; i++ {
		e := edits[i]
		switch e.kind {
		case opEqual:
			b.WriteByte(' ')
		case opDelete:
			b.WriteByte('-')
		case opInsert:
			b.WriteByte('+')
		}
		b.WriteString(e.line.text)
		b.WriteByte('\n')
		if !e.line.hasNewline {
			b.WriteString("\\ No newline at end of file\n")
		}
	}
}

// formatRange renders one side of a hunk header, following the convention that
// a count of one omits the count and a count of zero reports the line before
// the hunk.
func formatRange(start, count int) string {
	switch count {
	case 0:
		return strconv.Itoa(start-1) + ",0"
	case 1:
		return strconv.Itoa(start)
	default:
		return strconv.Itoa(start) + "," + strconv.Itoa(count)
	}
}

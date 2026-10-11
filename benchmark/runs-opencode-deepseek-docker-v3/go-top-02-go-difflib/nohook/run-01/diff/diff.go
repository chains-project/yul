// Package diff computes and formats unified diffs between two pieces of text.
package diff

import (
	"fmt"
	"strings"
)

// OpKind describes whether a line is unchanged, deleted from the old text, or
// inserted into the new text.
type OpKind int

const (
	// Equal marks a line present in both texts.
	Equal OpKind = iota
	// Delete marks a line present only in the old text.
	Delete
	// Insert marks a line present only in the new text.
	Insert
)

// Op is a single line-level edit operation.
type Op struct {
	Kind OpKind
	Text string
}

// Config controls how a unified diff is formatted.
type Config struct {
	// FromName and ToName label the old and new texts in the ---/+++ header.
	// Empty names default to "a" and "b".
	FromName string
	ToName   string
	// Context is the number of unchanged lines shown around each change.
	// Negative values are treated as zero.
	Context int
}

// Unified returns a unified diff between a and b using default labels ("a",
// "b") and three lines of context. It returns an empty string when a and b are
// identical.
func Unified(a, b string) string {
	return Config{Context: 3}.Unified(a, b)
}

// UnifiedNamed is like Unified but labels the old and new texts with the given
// names.
func UnifiedNamed(fromName, toName, a, b string) string {
	return Config{FromName: fromName, ToName: toName, Context: 3}.Unified(a, b)
}

// Unified renders a unified diff between a and b. The result is empty when the
// inputs are identical.
func (c Config) Unified(a, b string) string {
	oldLines := splitLines(a)
	newLines := splitLines(b)

	ops := computeOps(oldLines, newLines)
	lines := numberLines(ops)
	hunks := groupHunks(lines, max(c.Context, 0))
	if len(hunks) == 0 {
		return ""
	}

	fromName := c.FromName
	if fromName == "" {
		fromName = "a"
	}
	toName := c.ToName
	if toName == "" {
		toName = "b"
	}

	var sb strings.Builder
	fmt.Fprintf(&sb, "--- %s\n", fromName)
	fmt.Fprintf(&sb, "+++ %s\n", toName)
	for _, h := range hunks {
		writeHunk(&sb, lines, h)
	}
	return sb.String()
}

// unifiedLine is a formatted diff line carrying the source line numbers it
// corresponds to. For an inserted line oldNo is the old line the text would be
// inserted before (similarly for deleted lines and newNo).
type unifiedLine struct {
	tag    byte // ' ', '-', or '+'
	text   string
	oldNo  int
	newNo  int
	hasOld bool
	hasNew bool
}

func numberLines(ops []Op) []unifiedLine {
	lines := make([]unifiedLine, 0, len(ops))
	oldNo, newNo := 1, 1
	for _, op := range ops {
		switch op.Kind {
		case Equal:
			lines = append(lines, unifiedLine{
				tag: ' ', text: op.Text, oldNo: oldNo, newNo: newNo, hasOld: true, hasNew: true,
			})
			oldNo++
			newNo++
		case Delete:
			lines = append(lines, unifiedLine{
				tag: '-', text: op.Text, oldNo: oldNo, newNo: newNo, hasOld: true,
			})
			oldNo++
		case Insert:
			lines = append(lines, unifiedLine{
				tag: '+', text: op.Text, oldNo: oldNo, newNo: newNo, hasNew: true,
			})
			newNo++
		}
	}
	return lines
}

type hunk struct {
	start int // inclusive index into the numbered lines
	end   int // inclusive index into the numbered lines
}

// groupHunks collapses changed lines into hunks padded by context unchanged
// lines, merging hunks whose context would overlap.
func groupHunks(lines []unifiedLine, context int) []hunk {
	var changes []int
	for i, l := range lines {
		if l.tag != ' ' {
			changes = append(changes, i)
		}
	}
	if len(changes) == 0 {
		return nil
	}

	var hunks []hunk
	lo, hi := changes[0], changes[0]
	flush := func() {
		start := max(lo-context, 0)
		end := min(hi+context, len(lines)-1)
		hunks = append(hunks, hunk{start: start, end: end})
	}
	for _, c := range changes[1:] {
		if c-hi-1 <= 2*context {
			hi = c
			continue
		}
		flush()
		lo, hi = c, c
	}
	flush()
	return hunks
}

func writeHunk(sb *strings.Builder, lines []unifiedLine, h hunk) {
	oldStart, oldCount := rangeStart(lines, h, true)
	newStart, newCount := rangeStart(lines, h, false)

	fmt.Fprintf(sb, "@@ -%s +%s @@\n", formatRange(oldStart, oldCount), formatRange(newStart, newCount))
	for i := h.start; i <= h.end; i++ {
		line := lines[i]
		sb.WriteByte(line.tag)
		sb.WriteString(line.text)
		if !strings.HasSuffix(line.text, "\n") {
			sb.WriteByte('\n')
			sb.WriteString("\\ No newline at end of file\n")
		}
	}
}

// rangeStart returns the first line number and total line count for the old
// (oldSide true) or new (oldSide false) side of a hunk.
func rangeStart(lines []unifiedLine, h hunk, oldSide bool) (start, count int) {
	has := func(l unifiedLine) bool {
		if oldSide {
			return l.hasOld
		}
		return l.hasNew
	}
	num := func(l unifiedLine) int {
		if oldSide {
			return l.oldNo
		}
		return l.newNo
	}

	for i := h.start; i <= h.end; i++ {
		if has(lines[i]) {
			count++
		}
	}
	if count > 0 {
		for i := h.start; i <= h.end; i++ {
			if has(lines[i]) {
				return num(lines[i]), count
			}
		}
	}
	// No lines on this side: the range is empty and starts just before the
	// first line of the hunk.
	return num(lines[h.start]) - 1, 0
}

func formatRange(start, count int) string {
	if count == 1 {
		return fmt.Sprintf("%d", start)
	}
	return fmt.Sprintf("%d,%d", start, count)
}

// computeOps runs Myers' O(ND) diff algorithm over the two line slices and
// returns the edit script that turns a into b.
func computeOps(a, b []string) []Op {
	n, m := len(a), len(b)
	maxD := n + m
	offset := maxD + 1
	v := make([]int, 2*maxD+3)
	trace := make([][]int, 0, maxD+1)

	for d := 0; d <= maxD; d++ {
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
				return backtrack(trace, a, b, offset)
			}
		}
	}
	return nil
}

func backtrack(trace [][]int, a, b []string, offset int) []Op {
	x, y := len(a), len(b)
	ops := make([]Op, 0, x+y)

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
			ops = append(ops, Op{Kind: Equal, Text: a[x-1]})
			x--
			y--
		}
		if d > 0 {
			if x == prevX {
				ops = append(ops, Op{Kind: Insert, Text: b[prevY]})
			} else {
				ops = append(ops, Op{Kind: Delete, Text: a[prevX]})
			}
		}
		x, y = prevX, prevY
	}

	for i, j := 0, len(ops)-1; i < j; i, j = i+1, j-1 {
		ops[i], ops[j] = ops[j], ops[i]
	}
	return ops
}

// splitLines splits s into lines, keeping each line's trailing newline. A
// non-empty final line without a newline is returned as-is.
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

// Package diff computes line-based differences between two texts and
// renders them in unified diff format.
package diff

import (
	"fmt"
	"strings"
)

// Kind identifies the type of an edit operation.
type Kind int

const (
	Equal Kind = iota
	Delete
	Insert
)

// Op is a single line-level edit. A and B are 0-based line indexes into the
// old and new texts; only the index relevant to Kind is meaningful for
// Delete (A) and Insert (B).
type Op struct {
	Kind Kind
	A, B int
	Line string // includes the trailing "\n", if present
}

// Lines splits s into lines, keeping each line's trailing newline. The last
// line has no newline if s does not end with one.
func Lines(s string) []string {
	if s == "" {
		return nil
	}
	lines := strings.SplitAfter(s, "\n")
	if lines[len(lines)-1] == "" {
		lines = lines[:len(lines)-1]
	}
	return lines
}

// Edits returns a minimal edit script transforming a into b, using the
// Myers O(ND) algorithm after trimming any common prefix and suffix.
func Edits(a, b []string) []Op {
	var ops []Op

	pre := 0
	for pre < len(a) && pre < len(b) && a[pre] == b[pre] {
		ops = append(ops, Op{Equal, pre, pre, a[pre]})
		pre++
	}
	suf := 0
	for suf < len(a)-pre && suf < len(b)-pre && a[len(a)-1-suf] == b[len(b)-1-suf] {
		suf++
	}

	for _, op := range myers(a[pre:len(a)-suf], b[pre:len(b)-suf]) {
		op.A += pre
		op.B += pre
		ops = append(ops, op)
	}

	for i := suf; i > 0; i-- {
		ops = append(ops, Op{Equal, len(a) - i, len(b) - i, a[len(a)-i]})
	}
	return ops
}

func myers(a, b []string) []Op {
	n, m := len(a), len(b)
	if n == 0 && m == 0 {
		return nil
	}
	max := n + m
	off := max
	v := make([]int, 2*max+2)

	// trace[d] holds the furthest-reaching x per diagonal before round d.
	var trace [][]int
	for d := 0; d <= max; d++ {
		trace = append(trace, append([]int(nil), v...))
		done := false
		for k := -d; k <= d; k += 2 {
			var x int
			if k == -d || (k != d && v[off+k-1] < v[off+k+1]) {
				x = v[off+k+1]
			} else {
				x = v[off+k-1] + 1
			}
			y := x - k
			for x < n && y < m && a[x] == b[y] {
				x++
				y++
			}
			v[off+k] = x
			if x >= n && y >= m {
				done = true
				break
			}
		}
		if done {
			break
		}
	}

	// Walk the trace backwards to recover the path.
	var rev []Op
	x, y := n, m
	for d := len(trace) - 1; d >= 0; d-- {
		v := trace[d]
		k := x - y
		var prevK int
		if k == -d || (k != d && v[off+k-1] < v[off+k+1]) {
			prevK = k + 1
		} else {
			prevK = k - 1
		}
		prevX := v[off+prevK]
		prevY := prevX - prevK
		for x > prevX && y > prevY {
			x--
			y--
			rev = append(rev, Op{Equal, x, y, a[x]})
		}
		if d > 0 {
			if x == prevX {
				rev = append(rev, Op{Insert, x, prevY, b[prevY]})
			} else {
				rev = append(rev, Op{Delete, prevX, y, a[prevX]})
			}
			x, y = prevX, prevY
		}
	}

	ops := make([]Op, len(rev))
	for i, op := range rev {
		ops[len(rev)-1-i] = op
	}
	return ops
}

// Unified returns a unified diff of oldText and newText with the given
// number of context lines, labelling the sides oldName and newName.
// It returns "" if the texts are equal.
func Unified(oldName, newName, oldText, newText string, context int) string {
	if oldText == newText {
		return ""
	}
	if context < 0 {
		context = 0
	}
	ops := Edits(Lines(oldText), Lines(newText))

	var sb strings.Builder
	fmt.Fprintf(&sb, "--- %s\n+++ %s\n", oldName, newName)

	for i := 0; i < len(ops); {
		// Find the next change.
		for i < len(ops) && ops[i].Kind == Equal {
			i++
		}
		if i == len(ops) {
			break
		}
		start := max(i-context, 0)

		// Extend the hunk while changes are within 2*context lines of each other.
		end := i
		for j := i; j < len(ops); j++ {
			if ops[j].Kind != Equal {
				end = j + 1
			} else if j-end >= 2*context {
				break
			}
		}
		end = min(end+context, len(ops))

		writeHunk(&sb, ops[start:end])
		i = end
	}
	return sb.String()
}

func writeHunk(sb *strings.Builder, ops []Op) {
	// Position of the hunk in each file is where the first op sits.
	aStart, bStart := ops[0].A, ops[0].B
	aLen, bLen := 0, 0
	for _, op := range ops {
		switch op.Kind {
		case Equal:
			aLen++
			bLen++
		case Delete:
			aLen++
		case Insert:
			bLen++
		}
	}
	fmt.Fprintf(sb, "@@ -%s +%s @@\n", hunkRange(aStart, aLen), hunkRange(bStart, bLen))

	for _, op := range ops {
		prefix := " "
		switch op.Kind {
		case Delete:
			prefix = "-"
		case Insert:
			prefix = "+"
		}
		sb.WriteString(prefix)
		sb.WriteString(op.Line)
		if !strings.HasSuffix(op.Line, "\n") {
			sb.WriteString("\n\\ No newline at end of file\n")
		}
	}
}

// hunkRange formats a 0-based start and length per GNU diff conventions.
func hunkRange(start, length int) string {
	switch length {
	case 0:
		return fmt.Sprintf("%d,0", start)
	case 1:
		return fmt.Sprintf("%d", start+1)
	default:
		return fmt.Sprintf("%d,%d", start+1, length)
	}
}

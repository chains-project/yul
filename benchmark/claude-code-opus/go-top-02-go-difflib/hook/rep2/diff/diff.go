// Package diff computes line-based differences between two texts and
// renders them in unified diff format.
//
// The edit script is computed with Myers' O(ND) algorithm, so the result is
// a minimal sequence of line insertions and deletions.
package diff

import (
	"fmt"
	"strings"
)

// Kind identifies the type of an Edit.
type Kind int

const (
	Equal  Kind = iota // line present in both texts
	Delete             // line present only in the old text
	Insert             // line present only in the new text
)

func (k Kind) String() string {
	switch k {
	case Equal:
		return "Equal"
	case Delete:
		return "Delete"
	case Insert:
		return "Insert"
	}
	return fmt.Sprintf("Kind(%d)", int(k))
}

// Edit is a single step of an edit script transforming the old text into
// the new text.
type Edit struct {
	Kind Kind
	// OldIndex and NewIndex are the 0-based positions in the old and new
	// line slices at which this edit applies.
	OldIndex, NewIndex int
	// Line is the affected line, including its trailing newline if any.
	Line string
}

// Lines splits s into lines, keeping the trailing "\n" on each line. A final
// line without a newline is returned as-is, so strings.Join(Lines(s), "")
// always equals s.
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

// Edits returns a minimal edit script transforming a into b.
func Edits(a, b []string) []Edit {
	// Trim the common prefix and suffix; they are cheap to find and keep the
	// Myers search space small for the common case of localized changes.
	pre := 0
	for pre < len(a) && pre < len(b) && a[pre] == b[pre] {
		pre++
	}
	suf := 0
	for suf < len(a)-pre && suf < len(b)-pre && a[len(a)-1-suf] == b[len(b)-1-suf] {
		suf++
	}

	kinds := make([]Kind, 0, len(a)+len(b))
	for range pre {
		kinds = append(kinds, Equal)
	}
	kinds = append(kinds, myers(a[pre:len(a)-suf], b[pre:len(b)-suf])...)
	for range suf {
		kinds = append(kinds, Equal)
	}

	edits := make([]Edit, len(kinds))
	i, j := 0, 0
	for n, k := range kinds {
		e := Edit{Kind: k, OldIndex: i, NewIndex: j}
		switch k {
		case Equal:
			e.Line = a[i]
			i++
			j++
		case Delete:
			e.Line = a[i]
			i++
		case Insert:
			e.Line = b[j]
			j++
		}
		edits[n] = e
	}
	return edits
}

// myers returns the sequence of edit kinds of a shortest edit script
// transforming a into b.
func myers(a, b []string) []Kind {
	n, m := len(a), len(b)
	if n == 0 && m == 0 {
		return nil
	}
	max := n + m
	off := max + 1
	v := make([]int, 2*max+3) // v[off+k] = furthest x reached on diagonal k
	// trace[d] holds v[k] for k in [-d, d] after round d, at index k+d.
	var trace [][]int

	for d := 0; d <= max; d++ {
		done := false
		for k := -d; k <= d; k += 2 {
			var x int
			if k == -d || (k != d && v[off+k-1] < v[off+k+1]) {
				x = v[off+k+1] // move down: insertion
			} else {
				x = v[off+k-1] + 1 // move right: deletion
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
		trace = append(trace, append([]int(nil), v[off-d:off+d+1]...))
		if done {
			break
		}
	}

	// Walk back from (n, m) to (0, 0), emitting edits in reverse.
	var rev []Kind
	x, y := n, m
	for d := len(trace) - 1; d > 0; d-- {
		prev := trace[d-1] // index k+(d-1)
		k := x - y
		var pk int
		if k == -d || (k != d && prev[k-1+d-1] < prev[k+1+d-1]) {
			pk = k + 1
		} else {
			pk = k - 1
		}
		px := prev[pk+d-1]
		py := px - pk
		for x > px && y > py {
			rev = append(rev, Equal)
			x--
			y--
		}
		if pk == k+1 {
			rev = append(rev, Insert)
		} else {
			rev = append(rev, Delete)
		}
		x, y = px, py
	}
	for x > 0 {
		rev = append(rev, Equal)
		x--
	}

	for i, j := 0, len(rev)-1; i < j; i, j = i+1, j-1 {
		rev[i], rev[j] = rev[j], rev[i]
	}
	return rev
}

// Unified returns a unified diff transforming oldText into newText, using
// oldName and newName in the file headers and including context lines of
// unchanged text around each change. It returns "" if the texts are equal.
func Unified(oldName, newName, oldText, newText string, context int) string {
	if oldText == newText {
		return ""
	}
	if context < 0 {
		context = 0
	}
	edits := Edits(Lines(oldText), Lines(newText))

	var sb strings.Builder
	fmt.Fprintf(&sb, "--- %s\n+++ %s\n", oldName, newName)

	for i := 0; i < len(edits); {
		// Find the next change.
		for i < len(edits) && edits[i].Kind == Equal {
			i++
		}
		if i == len(edits) {
			break
		}
		start := max(i-context, 0)

		// Extend the hunk while the gap to the next change is small enough
		// that the context regions would touch or overlap.
		end := i
		for {
			for end < len(edits) && edits[end].Kind != Equal {
				end++
			}
			gap := end
			for gap < len(edits) && edits[gap].Kind == Equal {
				gap++
			}
			if gap == len(edits) || gap-end > 2*context {
				end = min(end+context, len(edits))
				break
			}
			end = gap
		}

		writeHunk(&sb, edits[start:end])
		i = end
	}
	return sb.String()
}

func writeHunk(sb *strings.Builder, h []Edit) {
	var oldLen, newLen int
	for _, e := range h {
		if e.Kind != Insert {
			oldLen++
		}
		if e.Kind != Delete {
			newLen++
		}
	}
	fmt.Fprintf(sb, "@@ -%s +%s @@\n",
		hunkRange(h[0].OldIndex, oldLen), hunkRange(h[0].NewIndex, newLen))

	for _, e := range h {
		switch e.Kind {
		case Equal:
			sb.WriteByte(' ')
		case Delete:
			sb.WriteByte('-')
		case Insert:
			sb.WriteByte('+')
		}
		sb.WriteString(e.Line)
		if !strings.HasSuffix(e.Line, "\n") {
			sb.WriteString("\n\\ No newline at end of file\n")
		}
	}
}

// hunkRange formats a hunk range the way GNU diff does: 1-based start line,
// with the length omitted when it is 1, and an empty range reported as
// starting at the line before it.
func hunkRange(start, n int) string {
	switch n {
	case 0:
		return fmt.Sprintf("%d,0", start)
	case 1:
		return fmt.Sprintf("%d", start+1)
	}
	return fmt.Sprintf("%d,%d", start+1, n)
}

package diff

import (
	"fmt"
	"math/rand"
	"strings"
	"testing"
)

func TestUnified(t *testing.T) {
	tests := []struct {
		name string
		old  string
		new  string
		opts Options
		want string
	}{
		{
			name: "identical",
			old:  "a\nb\nc\n",
			new:  "a\nb\nc\n",
			opts: Options{Context: DefaultContext},
			want: "",
		},
		{
			name: "single change",
			old:  "a\nb\nc\nd\ne\n",
			new:  "a\nb\nC\nd\ne\n",
			opts: Options{Context: DefaultContext},
			want: "--- old\n+++ new\n@@ -1,5 +1,5 @@\n a\n b\n-c\n+C\n d\n e\n",
		},
		{
			name: "separate hunks",
			old:  "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n",
			new:  "one\n2\n3\n4\n5\n6\n7\n8\n9\nten\n",
			opts: Options{Context: 1},
			want: "--- old\n+++ new\n" +
				"@@ -1,2 +1,2 @@\n-1\n+one\n 2\n" +
				"@@ -9,2 +9,2 @@\n 9\n-10\n+ten\n",
		},
		{
			name: "merged hunks",
			old:  "1\n2\n3\n4\n5\n",
			new:  "one\n2\n3\nfour\n5\n",
			opts: Options{Context: 1},
			want: "--- old\n+++ new\n@@ -1,5 +1,5 @@\n-1\n+one\n 2\n 3\n-4\n+four\n 5\n",
		},
		{
			name: "no trailing newline",
			old:  "a\nb",
			new:  "a\nB",
			opts: Options{Context: DefaultContext},
			want: "--- old\n+++ new\n@@ -1,2 +1,2 @@\n a\n-b\n\\ No newline at end of file\n" +
				"+B\n\\ No newline at end of file\n",
		},
		{
			name: "insertion at start",
			old:  "",
			new:  "x\n",
			opts: Options{Context: DefaultContext},
			want: "--- old\n+++ new\n@@ -0,0 +1 @@\n+x\n",
		},
		{
			name: "deletion of all",
			old:  "a\nb\n",
			new:  "",
			opts: Options{Context: DefaultContext},
			want: "--- old\n+++ new\n@@ -1,2 +0,0 @@\n-a\n-b\n",
		},
		{
			name: "custom labels and no context",
			old:  "a\nb\nc\n",
			new:  "a\nc\n",
			opts: Options{FromFile: "expected", ToFile: "actual", Context: 0},
			want: "--- expected\n+++ actual\n@@ -2 +1,0 @@\n-b\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := UnifiedWith(tt.old, tt.new, tt.opts); got != tt.want {
				t.Errorf("UnifiedWith() mismatch\n got:\n%s\nwant:\n%s", got, tt.want)
			}
		})
	}
}

func TestUnifiedReturnsEmptyForEqualText(t *testing.T) {
	if got := Unified("same\n", "same\n"); got != "" {
		t.Fatalf("Unified() = %q, want empty string", got)
	}
}

func TestSplitLines(t *testing.T) {
	tests := []struct {
		in   string
		want []line
	}{
		{"", nil},
		{"a", []line{{text: "a"}}},
		{"a\n", []line{{text: "a", hasNewline: true}}},
		{"a\nb", []line{{text: "a", hasNewline: true}, {text: "b"}}},
		{"a\nb\n", []line{{text: "a", hasNewline: true}, {text: "b", hasNewline: true}}},
		{"\n", []line{{text: "", hasNewline: true}}},
	}
	for _, tt := range tests {
		got := splitLines(tt.in)
		if len(got) != len(tt.want) {
			t.Fatalf("splitLines(%q) = %#v, want %#v", tt.in, got, tt.want)
		}
		for i := range got {
			if got[i] != tt.want[i] {
				t.Fatalf("splitLines(%q)[%d] = %#v, want %#v", tt.in, i, got[i], tt.want[i])
			}
		}
	}
}

// TestMyersFuzz checks that the edit script produced by myers is applicable
// and minimal for many random inputs.
func TestMyersFuzz(t *testing.T) {
	rng := rand.New(rand.NewSource(1))
	alphabet := []string{"a", "b", "c", "d"}

	for iter := 0; iter < 2000; iter++ {
		a := randomLines(rng, alphabet)
		b := randomLines(rng, alphabet)
		edits := myers(a, b)

		i, j := 0, 0
		changes := 0
		for _, e := range edits {
			switch e.kind {
			case opEqual:
				if i >= len(a) || j >= len(b) || a[i] != e.line || b[j] != e.line {
					t.Fatalf("iter %d: bad equal edit at a[%d], b[%d]: %#v", iter, i, j, e)
				}
				i++
				j++
			case opDelete:
				if i >= len(a) || a[i] != e.line {
					t.Fatalf("iter %d: bad delete edit at a[%d]: %#v", iter, i, e)
				}
				i++
				changes++
			case opInsert:
				if j >= len(b) || b[j] != e.line {
					t.Fatalf("iter %d: bad insert edit at b[%d]: %#v", iter, j, e)
				}
				j++
				changes++
			}
		}
		if i != len(a) || j != len(b) {
			t.Fatalf("iter %d: script consumed a[%d/%d] b[%d/%d]", iter, i, len(a), j, len(b))
		}

		if want := len(a) + len(b) - 2*lcsLen(a, b); changes != want {
			t.Fatalf("iter %d: edit distance %d, want minimal %d (a=%v b=%v)", iter, changes, want, a, b)
		}
	}
}

func randomLines(rng *rand.Rand, alphabet []string) []line {
	n := rng.Intn(12)
	lines := make([]line, n)
	for i := range lines {
		lines[i] = line{text: alphabet[rng.Intn(len(alphabet))], hasNewline: true}
	}
	return lines
}

func lcsLen(a, b []line) int {
	dp := make([][]int, len(a)+1)
	for i := range dp {
		dp[i] = make([]int, len(b)+1)
	}
	for i := 1; i <= len(a); i++ {
		for j := 1; j <= len(b); j++ {
			switch {
			case a[i-1] == b[j-1]:
				dp[i][j] = dp[i-1][j-1] + 1
			case dp[i-1][j] >= dp[i][j-1]:
				dp[i][j] = dp[i-1][j]
			default:
				dp[i][j] = dp[i][j-1]
			}
		}
	}
	return dp[len(a)][len(b)]
}

func ExampleUnified() {
	oldText := "hello\nworld\n"
	newText := "hello\nthere\n"
	fmt.Print(UnifiedWith(oldText, newText, Options{FromFile: "old", ToFile: "new", Context: 1}))
	// Output:
	// --- old
	// +++ new
	// @@ -1,2 +1,2 @@
	//  hello
	// -world
	// +there
}

func TestHunksDoNotOverlap(t *testing.T) {
	oldText := strings.Repeat("keep\n", 20)
	newText := strings.Replace(oldText, "keep\n", "change\n", 1)
	got := UnifiedWith(oldText, newText, Options{Context: 2})
	want := "--- old\n+++ new\n@@ -1,3 +1,3 @@\n-keep\n+change\n keep\n keep\n"
	if got != want {
		t.Fatalf("UnifiedWith() mismatch\n got:\n%s\nwant:\n%s", got, want)
	}
}

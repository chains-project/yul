package diff

import (
	"math/rand"
	"strings"
	"testing"
)

func TestLines(t *testing.T) {
	tests := []struct {
		in   string
		want []string
	}{
		{"", nil},
		{"a", []string{"a"}},
		{"a\n", []string{"a\n"}},
		{"a\nb", []string{"a\n", "b"}},
		{"a\n\nb\n", []string{"a\n", "\n", "b\n"}},
	}
	for _, tt := range tests {
		got := Lines(tt.in)
		if strings.Join(got, "|") != strings.Join(tt.want, "|") || len(got) != len(tt.want) {
			t.Errorf("Lines(%q) = %q, want %q", tt.in, got, tt.want)
		}
	}
}

func TestUnified(t *testing.T) {
	tests := []struct {
		name     string
		old, new string
		context  int
		want     string
	}{
		{
			name: "equal",
			old:  "a\nb\n",
			new:  "a\nb\n",
			want: "",
		},
		{
			name:    "single change",
			old:     "a\nb\nc\n",
			new:     "a\nB\nc\n",
			context: 3,
			want: `--- old
+++ new
@@ -1,3 +1,3 @@
 a
-b
+B
 c
`,
		},
		{
			name:    "empty to text",
			old:     "",
			new:     "a\nb\n",
			context: 3,
			want: `--- old
+++ new
@@ -0,0 +1,2 @@
+a
+b
`,
		},
		{
			name:    "text to empty",
			old:     "a\n",
			new:     "",
			context: 3,
			want: `--- old
+++ new
@@ -1 +0,0 @@
-a
`,
		},
		{
			name:    "missing final newline",
			old:     "a\nb",
			new:     "a\nb\n",
			context: 3,
			want: `--- old
+++ new
@@ -1,2 +1,2 @@
 a
-b
\ No newline at end of file
+b
`,
		},
		{
			name:    "separate hunks",
			old:     "1\n2\n3\n4\n5\n6\n7\n8\n9\n",
			new:     "1\nX\n3\n4\n5\n6\n7\nY\n9\n",
			context: 1,
			want: `--- old
+++ new
@@ -1,3 +1,3 @@
 1
-2
+X
 3
@@ -7,3 +7,3 @@
 7
-8
+Y
 9
`,
		},
		{
			name:    "merged hunks",
			old:     "1\n2\n3\n4\n5\n6\n",
			new:     "1\nX\n3\n4\nY\n6\n",
			context: 1,
			want: `--- old
+++ new
@@ -1,6 +1,6 @@
 1
-2
+X
 3
 4
-5
+Y
 6
`,
		},
		{
			name:    "zero context insertion",
			old:     "a\nb\n",
			new:     "a\nx\nb\n",
			context: 0,
			want: `--- old
+++ new
@@ -1,0 +2 @@
+x
`,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := Unified("old", "new", tt.old, tt.new, tt.context)
			if got != tt.want {
				t.Errorf("got:\n%s\nwant:\n%s", got, tt.want)
			}
		})
	}
}

// TestEditsRandom checks that random edit scripts reconstruct both inputs
// and are no longer than the known LCS-based minimum.
func TestEditsRandom(t *testing.T) {
	rng := rand.New(rand.NewSource(1))
	gen := func() []string {
		s := make([]string, rng.Intn(30))
		for i := range s {
			s[i] = string(rune('a' + rng.Intn(4)))
		}
		return s
	}
	for iter := 0; iter < 2000; iter++ {
		a, b := gen(), gen()
		edits := Edits(a, b)

		var gotA, gotB []string
		changes := 0
		for _, e := range edits {
			if e.Kind != Insert {
				gotA = append(gotA, e.Line)
			}
			if e.Kind != Delete {
				gotB = append(gotB, e.Line)
			}
			if e.Kind != Equal {
				changes++
			}
		}
		if strings.Join(gotA, "") != strings.Join(a, "") || strings.Join(gotB, "") != strings.Join(b, "") {
			t.Fatalf("edits do not reconstruct inputs\na=%q\nb=%q\nedits=%v", a, b, edits)
		}
		if want := len(a) + len(b) - 2*lcs(a, b); changes != want {
			t.Fatalf("got %d changes, want minimal %d\na=%q\nb=%q", changes, want, a, b)
		}
	}
}

func lcs(a, b []string) int {
	dp := make([][]int, len(a)+1)
	for i := range dp {
		dp[i] = make([]int, len(b)+1)
	}
	for i := len(a) - 1; i >= 0; i-- {
		for j := len(b) - 1; j >= 0; j-- {
			if a[i] == b[j] {
				dp[i][j] = dp[i+1][j+1] + 1
			} else {
				dp[i][j] = max(dp[i+1][j], dp[i][j+1])
			}
		}
	}
	return dp[0][0]
}

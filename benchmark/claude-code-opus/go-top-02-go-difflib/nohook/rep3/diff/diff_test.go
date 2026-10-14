package diff

import (
	"strings"
	"testing"
)

func TestUnifiedEqual(t *testing.T) {
	if got := Unified("a", "b", "same\n", "same\n", -1); got != "" {
		t.Fatalf("expected empty diff, got:\n%s", got)
	}
}

func TestUnified(t *testing.T) {
	old := "one\ntwo\nthree\nfour\n"
	new := "one\n2\nthree\nfour\nfive\n"
	want := `--- old
+++ new
@@ -1,4 +1,5 @@
 one
-two
+2
 three
 four
+five
`
	if got := Unified("old", "new", old, new, -1); got != want {
		t.Fatalf("diff mismatch\ngot:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedNoTrailingNewline(t *testing.T) {
	want := `--- old
+++ new
@@ -1 +1 @@
-a
+a
\ No newline at end of file
`
	if got := Unified("old", "new", "a\n", "a", -1); got != want {
		t.Fatalf("diff mismatch\ngot:\n%s\nwant:\n%s", got, want)
	}
}

func TestColorize(t *testing.T) {
	out := Colorize(Unified("old", "new", "x\n", "y\n", -1))
	for _, want := range []string{ansiRed + "-x" + ansiReset, ansiGreen + "+y" + ansiReset, ansiCyan + "@@"} {
		if !strings.Contains(out, want) {
			t.Errorf("colorized output missing %q:\n%q", want, out)
		}
	}
}

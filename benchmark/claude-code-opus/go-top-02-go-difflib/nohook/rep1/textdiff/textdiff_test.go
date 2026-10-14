package textdiff

import (
	"strings"
	"testing"
)

func TestUnifiedIdentical(t *testing.T) {
	if got := Unified("a\nb\n", "a\nb\n"); got != "" {
		t.Fatalf("expected empty diff, got:\n%s", got)
	}
}

func TestUnified(t *testing.T) {
	oldText := "one\ntwo\nthree\n"
	newText := "one\n2\nthree\nfour\n"
	want := `--- old
+++ new
@@ -1,3 +1,4 @@
 one
-two
+2
 three
+four
`
	if got := Unified(oldText, newText); got != want {
		t.Fatalf("diff mismatch\ngot:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedWithLabelsAndContext(t *testing.T) {
	oldText := "a\nb\nc\nd\ne\n"
	newText := "a\nb\nX\nd\ne\n"
	got := UnifiedWith(oldText, newText, Options{OldLabel: "want", NewLabel: "got", Context: 0})
	want := `--- want
+++ got
@@ -3 +3 @@
-c
+X
`
	if got != want {
		t.Fatalf("diff mismatch\ngot:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedMissingTrailingNewline(t *testing.T) {
	got := Unified("a\n", "a")
	if !strings.Contains(got, `\ No newline at end of file`) {
		t.Fatalf("expected no-newline marker, got:\n%s", got)
	}
}

func TestColor(t *testing.T) {
	got := UnifiedWith("x\n", "y\n", Options{Context: -1, Color: true})
	for _, s := range []string{ansiRed + "-x" + ansiReset, ansiGreen + "+y" + ansiReset, ansiCyan + "@@"} {
		if !strings.Contains(got, s) {
			t.Errorf("missing %q in:\n%q", s, got)
		}
	}
}

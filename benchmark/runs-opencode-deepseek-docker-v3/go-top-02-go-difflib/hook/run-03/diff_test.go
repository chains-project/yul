package difftool

import (
	"strings"
	"testing"
)

func TestUnifiedIdentical(t *testing.T) {
	text := "alpha\nbeta\ngamma\n"
	got, err := UnifiedText(text, text)
	if err != nil {
		t.Fatalf("UnifiedText returned error: %v", err)
	}
	if got != "" {
		t.Fatalf("expected empty diff for identical texts, got:\n%s", got)
	}
}

func TestUnifiedChangedLine(t *testing.T) {
	from := "one\ntwo\nthree\n"
	to := "one\n2\nthree\n"

	got, err := Unified(from, to, Options{FromFile: "a", ToFile: "b"})
	if err != nil {
		t.Fatalf("Unified returned error: %v", err)
	}

	want := "--- a\n" +
		"+++ b\n" +
		"@@ -1,3 +1,3 @@\n" +
		" one\n" +
		"-two\n" +
		"+2\n" +
		" three\n"

	if got != want {
		t.Fatalf("unexpected diff:\ngot:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedContext(t *testing.T) {
	from := "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n"
	to := "1\n2\n3\n4\n5\n6\n7\n8\n9\nTEN\n"

	got, err := Unified(from, to, Options{FromFile: "a", ToFile: "b", Context: 1})
	if err != nil {
		t.Fatalf("Unified returned error: %v", err)
	}

	want := "--- a\n" +
		"+++ b\n" +
		"@@ -9,2 +9,2 @@\n" +
		" 9\n" +
		"-10\n" +
		"+TEN\n"

	if got != want {
		t.Fatalf("unexpected diff:\ngot:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedSubset(t *testing.T) {
	from := "a\nb\nc\nd\ne\n"
	to := "a\nb\nX\nd\ne\n"

	got, err := UnifiedText(from, to)
	if err != nil {
		t.Fatalf("UnifiedText returned error: %v", err)
	}
	if !strings.Contains(got, "-c\n") || !strings.Contains(got, "+X\n") {
		t.Fatalf("diff does not contain the changed lines:\n%s", got)
	}
}

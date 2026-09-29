package difftool

import (
	"bytes"
	"strings"
	"testing"
)

func TestUnifiedIdentical(t *testing.T) {
	if got := Unified("same\ntext\n", "same\ntext\n"); got != "" {
		t.Fatalf("Unified() = %q, want empty string", got)
	}
}

func TestUnified(t *testing.T) {
	got := Unified("a\nb\nc\n", "a\nB\nc\n")
	want := strings.Join([]string{
		"--- expected",
		"+++ actual",
		"@@ -1,3 +1,3 @@",
		" a",
		"-b",
		"+B",
		" c",
		"",
	}, "\n")
	if got != want {
		t.Fatalf("Unified() =\n%s\nwant:\n%s", got, want)
	}
}

func TestRenderLabels(t *testing.T) {
	got, err := Render(Options{FromFile: "want", ToFile: "got"}, "x\n", "y\n")
	if err != nil {
		t.Fatal(err)
	}
	if !strings.HasPrefix(got, "--- want\n+++ got\n") {
		t.Fatalf("Render() = %q, want want/got headers", got)
	}
}

func TestRenderContext(t *testing.T) {
	a := "1\n2\n3\n4\n5\n6\n7\n8\n9\n"
	b := "1\n2\n3\n4\nX\n6\n7\n8\n9\n"

	got, err := Render(Options{Context: 1}, a, b)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(got, " 9") || !strings.Contains(got, " 4") {
		t.Fatalf("Render(Context:1) = %q, want only one context line", got)
	}
}

func TestRenderMissingTrailingNewline(t *testing.T) {
	got, err := Render(Options{}, "a", "b")
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(got, "-a") || !strings.Contains(got, "+b") {
		t.Fatalf("Render() = %q, want -a/+b", got)
	}
}

func TestWriteIdenticalWritesNothing(t *testing.T) {
	var buf bytes.Buffer
	if err := Write(&buf, Options{}, "same\n", "same\n"); err != nil {
		t.Fatal(err)
	}
	if buf.Len() != 0 {
		t.Fatalf("Write() wrote %q, want nothing", buf.String())
	}
}

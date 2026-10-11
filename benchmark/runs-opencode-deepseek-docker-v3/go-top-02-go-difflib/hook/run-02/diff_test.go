package difftool

import (
	"bytes"
	"strings"
	"testing"
)

func TestUnifiedChangedLine(t *testing.T) {
	got, err := Unified("hello\nworld\n", "hello\nthere\n", Options{
		FromFile: "old.txt",
		ToFile:   "new.txt",
	})
	if err != nil {
		t.Fatalf("Unified returned error: %v", err)
	}
	want := "--- old.txt\n+++ new.txt\n@@ -1,2 +1,2 @@\n hello\n-world\n+there\n"
	if got != want {
		t.Fatalf("unexpected diff:\n got %q\nwant %q", got, want)
	}
}

func TestUnifiedIdentical(t *testing.T) {
	got, err := Unified("same\ntext\n", "same\ntext\n", Options{})
	if err != nil {
		t.Fatalf("Unified returned error: %v", err)
	}
	if got != "" {
		t.Fatalf("expected empty diff, got %q", got)
	}
}

func TestUnifiedContext(t *testing.T) {
	from := "a\nb\nc\nd\ne\nf\ng\n"
	to := "a\nb\nc\nX\ne\nf\ng\n"
	got, err := Unified(from, to, Options{Context: 1})
	if err != nil {
		t.Fatalf("Unified returned error: %v", err)
	}
	if !strings.Contains(got, "@@ -3,3 +3,3 @@") {
		t.Fatalf("expected one-line context hunk, got:\n%s", got)
	}
	if strings.Contains(got, "-a") || !strings.Contains(got, "-d") || !strings.Contains(got, "+X") {
		t.Fatalf("unexpected diff body:\n%s", got)
	}
}

func TestWriteUnified(t *testing.T) {
	var buf bytes.Buffer
	if err := WriteUnified(&buf, "a\n", "b\n", Options{FromFile: "a", ToFile: "b"}); err != nil {
		t.Fatalf("WriteUnified returned error: %v", err)
	}
	got, err := Unified("a\n", "b\n", Options{FromFile: "a", ToFile: "b"})
	if err != nil {
		t.Fatalf("Unified returned error: %v", err)
	}
	if buf.String() != got {
		t.Fatalf("WriteUnified wrote %q, want %q", buf.String(), got)
	}
}

func TestEqual(t *testing.T) {
	if !Equal("x", "x") {
		t.Fatal("Equal returned false for identical text")
	}
	if Equal("x", "y") {
		t.Fatal("Equal returned true for different text")
	}
}

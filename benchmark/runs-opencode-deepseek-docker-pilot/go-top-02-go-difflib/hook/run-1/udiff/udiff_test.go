package udiff

import (
	"bytes"
	"strings"
	"testing"
)

func TestUnifiedIdentical(t *testing.T) {
	got, err := Unified("same\nlines\n", "same\nlines\n", nil)
	if err != nil {
		t.Fatalf("Unified: %v", err)
	}
	if got != "" {
		t.Fatalf("Unified identical = %q, want empty", got)
	}
}

func TestUnifiedChange(t *testing.T) {
	got, err := Unified("a\nb\nc\n", "a\nB\nc\n", &Options{
		FromFile: "old.txt",
		ToFile:   "new.txt",
		Context:  1,
	})
	if err != nil {
		t.Fatalf("Unified: %v", err)
	}
	for _, want := range []string{
		"--- old.txt\n",
		"+++ new.txt\n",
		"@@ -1,3 +1,3 @@\n",
		" a\n",
		"-b\n",
		"+B\n",
		" c\n",
	} {
		if !strings.Contains(got, want) {
			t.Errorf("diff missing %q:\n%s", want, got)
		}
	}
}

func TestUnifiedDefaults(t *testing.T) {
	got, err := Unified("x\n", "y\n", nil)
	if err != nil {
		t.Fatalf("Unified: %v", err)
	}
	if !strings.HasPrefix(got, "--- a\n+++ b\n") {
		t.Errorf("default labels missing:\n%s", got)
	}
}

func TestWriteUnified(t *testing.T) {
	var changed bytes.Buffer
	n, err := WriteUnified(&changed, "a\n", "b\n", nil)
	if err != nil {
		t.Fatalf("WriteUnified: %v", err)
	}
	if n == 0 || changed.Len() != n {
		t.Errorf("WriteUnified wrote %d bytes, buffer has %d", n, changed.Len())
	}

	var same bytes.Buffer
	if n, err := WriteUnified(&same, "a\n", "a\n", nil); err != nil || n != 0 || same.Len() != 0 {
		t.Errorf("WriteUnified on identical = (%d, %v), buffer %q; want (0, nil, \"\")", n, err, same.String())
	}
}

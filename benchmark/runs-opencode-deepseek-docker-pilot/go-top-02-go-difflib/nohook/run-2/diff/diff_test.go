package diff

import (
	"strings"
	"testing"
)

func TestUnifiedIdentical(t *testing.T) {
	got, err := Unified("hello\nworld\n", "hello\nworld\n")
	if err != nil {
		t.Fatalf("Unified returned error: %v", err)
	}
	if got != "" {
		t.Fatalf("expected empty diff for identical input, got:\n%s", got)
	}
}

func TestUnifiedChange(t *testing.T) {
	oldText := "alpha\nbravo\ncharlie\n"
	newText := "alpha\nBRAVO\ncharlie\n"

	got, err := UnifiedWithOptions(oldText, newText, Options{
		FromFile: "old.txt",
		ToFile:   "new.txt",
	})
	if err != nil {
		t.Fatalf("UnifiedWithOptions returned error: %v", err)
	}

	for _, want := range []string{
		"--- old.txt",
		"+++ new.txt",
		"-bravo",
		"+BRAVO",
		" alpha",
		" charlie",
	} {
		if !strings.Contains(got, want) {
			t.Errorf("diff missing %q; got:\n%s", want, got)
		}
	}
}

func TestUnifiedContext(t *testing.T) {
	var b strings.Builder
	for i := 0; i < 20; i++ {
		b.WriteString("line\n")
	}
	oldText := b.String()
	newText := strings.Replace(oldText, "line\n", "LINE\n", 1)

	got, err := UnifiedWithOptions(oldText, newText, Options{Context: 1})
	if err != nil {
		t.Fatalf("UnifiedWithOptions returned error: %v", err)
	}

	if strings.Count(got, "\n line") != 1 {
		t.Errorf("expected a single context line with Context=1, got:\n%s", got)
	}
	if !strings.Contains(got, "-line") || !strings.Contains(got, "+LINE") {
		t.Errorf("diff missing change lines, got:\n%s", got)
	}
}

func TestEqual(t *testing.T) {
	if !Equal("same", "same") {
		t.Error("Equal returned false for identical input")
	}
	if Equal("a", "b") {
		t.Error("Equal returned true for different input")
	}
}

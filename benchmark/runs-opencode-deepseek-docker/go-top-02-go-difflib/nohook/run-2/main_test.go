package main

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func writeTemp(t *testing.T, name, content string) string {
	t.Helper()
	path := filepath.Join(t.TempDir(), name)
	if err := os.WriteFile(path, []byte(content), 0o600); err != nil {
		t.Fatalf("writing %s: %v", name, err)
	}
	return path
}

func TestRunDifference(t *testing.T) {
	oldPath := writeTemp(t, "old.txt", "alpha\nbravo\ncharlie\n")
	newPath := writeTemp(t, "new.txt", "alpha\nBRAVO\ncharlie\n")

	var stdout, stderr bytes.Buffer
	code := run([]string{oldPath, newPath}, &stdout, &stderr)

	if code != 1 {
		t.Fatalf("exit code = %d, want 1 (stderr: %s)", code, stderr.String())
	}
	out := stdout.String()
	for _, want := range []string{"--- " + oldPath, "+++ " + newPath, "-bravo", "+BRAVO"} {
		if !strings.Contains(out, want) {
			t.Errorf("output missing %q; got:\n%s", want, out)
		}
	}
}

func TestRunEqual(t *testing.T) {
	path := writeTemp(t, "same.txt", "alpha\nbravo\n")

	var stdout, stderr bytes.Buffer
	code := run([]string{path, path}, &stdout, &stderr)

	if code != 0 {
		t.Fatalf("exit code = %d, want 0 (stderr: %s)", code, stderr.String())
	}
	if stdout.Len() != 0 {
		t.Errorf("expected no output, got:\n%s", stdout.String())
	}
}

func TestRunBothStdin(t *testing.T) {
	var stdout, stderr bytes.Buffer
	code := run([]string{"-", "-"}, &stdout, &stderr)

	if code != 2 {
		t.Fatalf("exit code = %d, want 2", code)
	}
}

func TestRunMissingArgs(t *testing.T) {
	var stdout, stderr bytes.Buffer
	code := run(nil, &stdout, &stderr)

	if code != 2 {
		t.Fatalf("exit code = %d, want 2", code)
	}
}

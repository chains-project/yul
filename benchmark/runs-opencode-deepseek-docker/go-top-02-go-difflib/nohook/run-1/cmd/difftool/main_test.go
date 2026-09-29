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
		t.Fatal(err)
	}
	return path
}

func TestRunUsage(t *testing.T) {
	var stdout, stderr bytes.Buffer
	if got := run(nil, &stdout, &stderr); got != 2 {
		t.Fatalf("run() = %d, want 2", got)
	}
	if !strings.Contains(stderr.String(), "usage:") {
		t.Fatalf("stderr = %q, want usage", stderr.String())
	}
}

func TestRunIdentical(t *testing.T) {
	a := writeTemp(t, "a.txt", "same\n")
	b := writeTemp(t, "b.txt", "same\n")

	var stdout, stderr bytes.Buffer
	if got := run([]string{a, b}, &stdout, &stderr); got != 0 {
		t.Fatalf("run() = %d, want 0 (stderr: %s)", got, stderr.String())
	}
	if stdout.Len() != 0 {
		t.Fatalf("stdout = %q, want empty", stdout.String())
	}
}

func TestRunDifferent(t *testing.T) {
	a := writeTemp(t, "a.txt", "one\ntwo\n")
	b := writeTemp(t, "b.txt", "one\nTWO\n")

	var stdout, stderr bytes.Buffer
	if got := run([]string{a, b}, &stdout, &stderr); got != 1 {
		t.Fatalf("run() = %d, want 1 (stderr: %s)", got, stderr.String())
	}
	out := stdout.String()
	if !strings.Contains(out, "-two") || !strings.Contains(out, "+TWO") {
		t.Fatalf("stdout = %q, want -two/+TWO", out)
	}
}

func TestRunMissingFile(t *testing.T) {
	a := writeTemp(t, "a.txt", "one\n")

	var stdout, stderr bytes.Buffer
	if got := run([]string{a, filepath.Join(t.TempDir(), "missing")}, &stdout, &stderr); got != 2 {
		t.Fatalf("run() = %d, want 2", got)
	}
}

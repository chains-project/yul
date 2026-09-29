package main

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestRunSameInputs(t *testing.T) {
	dir := t.TempDir()
	a := writeFile(t, dir, "a.txt", "same\n")
	b := writeFile(t, dir, "b.txt", "same\n")

	var stdout, stderr bytes.Buffer
	if code := run([]string{a, b}, strings.NewReader(""), &stdout, &stderr); code != exitSame {
		t.Fatalf("exit = %d, want %d (stderr: %s)", code, exitSame, stderr.String())
	}
	if stdout.Len() != 0 {
		t.Fatalf("expected no output, got %q", stdout.String())
	}
}

func TestRunDifferentInputs(t *testing.T) {
	dir := t.TempDir()
	a := writeFile(t, dir, "a.txt", "one\n")
	b := writeFile(t, dir, "b.txt", "two\n")

	var stdout, stderr bytes.Buffer
	code := run([]string{a, b}, strings.NewReader(""), &stdout, &stderr)
	if code != exitDiffer {
		t.Fatalf("exit = %d, want %d (stderr: %s)", code, exitDiffer, stderr.String())
	}
	want := "--- " + a + "\n+++ " + b + "\n@@ -1 +1 @@\n-one\n+two\n"
	if stdout.String() != want {
		t.Fatalf("got:\n%s\nwant:\n%s", stdout.String(), want)
	}
}

func TestRunStdin(t *testing.T) {
	dir := t.TempDir()
	b := writeFile(t, dir, "b.txt", "new\n")

	var stdout, stderr bytes.Buffer
	code := run([]string{"-", b}, strings.NewReader("old\n"), &stdout, &stderr)
	if code != exitDiffer {
		t.Fatalf("exit = %d, want %d (stderr: %s)", code, exitDiffer, stderr.String())
	}
	want := "--- stdin\n+++ " + b + "\n@@ -1 +1 @@\n-old\n+new\n"
	if stdout.String() != want {
		t.Fatalf("got:\n%s\nwant:\n%s", stdout.String(), want)
	}
}

func TestRunBothStdinRejected(t *testing.T) {
	var stdout, stderr bytes.Buffer
	if code := run([]string{"-", "-"}, strings.NewReader(""), &stdout, &stderr); code != exitError {
		t.Fatalf("exit = %d, want %d", code, exitError)
	}
}

func writeFile(t *testing.T, dir, name, content string) string {
	t.Helper()
	path := filepath.Join(dir, name)
	if err := os.WriteFile(path, []byte(content), 0o600); err != nil {
		t.Fatal(err)
	}
	return path
}

package main

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func writeFile(t *testing.T, dir, name, content string) string {
	t.Helper()
	path := filepath.Join(dir, name)
	if err := os.WriteFile(path, []byte(content), 0o600); err != nil {
		t.Fatalf("writing %s: %v", path, err)
	}
	return path
}

func TestRunIdenticalFiles(t *testing.T) {
	dir := t.TempDir()
	a := writeFile(t, dir, "a.txt", "same\n")
	b := writeFile(t, dir, "b.txt", "same\n")

	var stdout, stderr bytes.Buffer
	code := run([]string{a, b}, strings.NewReader(""), &stdout, &stderr)

	if code != 0 {
		t.Fatalf("exit code = %d, want 0 (stderr: %s)", code, stderr.String())
	}
	if stdout.Len() != 0 {
		t.Fatalf("expected no output, got: %q", stdout.String())
	}
}

func TestRunDifferentFiles(t *testing.T) {
	dir := t.TempDir()
	a := writeFile(t, dir, "a.txt", "one\ntwo\nthree\n")
	b := writeFile(t, dir, "b.txt", "one\n2\nthree\n")

	var stdout, stderr bytes.Buffer
	code := run([]string{a, b}, strings.NewReader(""), &stdout, &stderr)

	if code != 1 {
		t.Fatalf("exit code = %d, want 1 (stderr: %s)", code, stderr.String())
	}
	if !strings.Contains(stdout.String(), "-two") || !strings.Contains(stdout.String(), "+2") {
		t.Fatalf("output missing changed lines:\n%s", stdout.String())
	}
}

func TestRunStdin(t *testing.T) {
	dir := t.TempDir()
	b := writeFile(t, dir, "b.txt", "hello\n")

	var stdout, stderr bytes.Buffer
	code := run([]string{"-", b}, strings.NewReader("hello\n"), &stdout, &stderr)

	if code != 0 {
		t.Fatalf("exit code = %d, want 0 (stderr: %s)", code, stderr.String())
	}
}

func TestRunMissingFile(t *testing.T) {
	dir := t.TempDir()
	a := writeFile(t, dir, "a.txt", "x\n")

	var stdout, stderr bytes.Buffer
	code := run([]string{a, filepath.Join(dir, "missing.txt")}, strings.NewReader(""), &stdout, &stderr)

	if code != 2 {
		t.Fatalf("exit code = %d, want 2", code)
	}
	if !strings.Contains(stderr.String(), "no such file") {
		t.Fatalf("stderr = %q, want a file error", stderr.String())
	}
}

func TestRunWrongArgCount(t *testing.T) {
	var stdout, stderr bytes.Buffer
	code := run([]string{"only-one"}, strings.NewReader(""), &stdout, &stderr)

	if code != 2 {
		t.Fatalf("exit code = %d, want 2", code)
	}
}

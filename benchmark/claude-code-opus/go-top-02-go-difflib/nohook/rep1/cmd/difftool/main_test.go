package main

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestRun(t *testing.T) {
	dir := t.TempDir()
	a := filepath.Join(dir, "a.txt")
	b := filepath.Join(dir, "b.txt")
	os.WriteFile(a, []byte("hello\nworld\n"), 0o644)
	os.WriteFile(b, []byte("hello\ngophers\n"), 0o644)

	var out, errOut bytes.Buffer
	if code := run([]string{a, b}, nil, &out, &errOut); code != 1 {
		t.Fatalf("exit code = %d, want 1 (stderr: %s)", code, errOut.String())
	}
	if !strings.Contains(out.String(), "-world\n+gophers\n") {
		t.Fatalf("unexpected output:\n%s", out.String())
	}

	out.Reset()
	if code := run([]string{a, "-"}, strings.NewReader("hello\nworld\n"), &out, &errOut); code != 0 {
		t.Fatalf("identical inputs: exit code = %d, want 0", code)
	}
	if out.Len() != 0 {
		t.Fatalf("identical inputs produced output:\n%s", out.String())
	}

	if code := run([]string{a}, nil, &out, &errOut); code != 2 {
		t.Fatalf("bad args: exit code = %d, want 2", code)
	}
}

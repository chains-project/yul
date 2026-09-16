package main

import (
	"os"
	"os/exec"
	"testing"
)

func TestUnifiedDiff(t *testing.T) {
	a, err := os.CreateTemp("", "diff-test-a-")
	if err != nil {
		t.Fatal(err)
	}
	defer os.Remove(a.Name())

	b, err := os.CreateTemp("", "diff-test-b-")
	if err != nil {
		t.Fatal(err)
	}
	defer os.Remove(b.Name())

	a.WriteString("line one\nline two\nline three\n")
	b.WriteString("line one\nmodified two\nline three\nline four\n")

	cmd := exec.Command("go", "run", ".", "-a", a.Name(), "-b", b.Name())
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("diff command failed: %v\noutput: %s", err, string(output))
	}

	result := string(output)
	if len(result) == 0 {
		t.Fatal("expected diff output, got empty string")
	}

	t.Logf("Diff output:\n%s", result)
}
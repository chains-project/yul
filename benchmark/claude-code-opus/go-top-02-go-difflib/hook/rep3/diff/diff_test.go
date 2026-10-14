package diff

import (
	"math/rand"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func TestUnified(t *testing.T) {
	tests := []struct {
		name     string
		old, new string
		want     string
	}{
		{"equal", "a\nb\n", "a\nb\n", ""},
		{"change", "a\nb\nc\n", "a\nB\nc\n",
			"--- old\n+++ new\n@@ -1,3 +1,3 @@\n a\n-b\n+B\n c\n"},
		{"empty to text", "", "x\n",
			"--- old\n+++ new\n@@ -0,0 +1 @@\n+x\n"},
		{"text to empty", "x\ny\n", "",
			"--- old\n+++ new\n@@ -1,2 +0,0 @@\n-x\n-y\n"},
		{"missing final newline", "a\nb", "a\nb\n",
			"--- old\n+++ new\n@@ -1,2 +1,2 @@\n a\n-b\n\\ No newline at end of file\n+b\n"},
		{"two hunks", "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n", "X\n2\n3\n4\n5\n6\n7\n8\n9\nY\n",
			"--- old\n+++ new\n@@ -1,4 +1,4 @@\n-1\n+X\n 2\n 3\n 4\n@@ -7,4 +7,4 @@\n 7\n 8\n 9\n-10\n+Y\n"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := Unified("old", "new", tt.old, tt.new, 3)
			if got != tt.want {
				t.Errorf("Unified mismatch\ngot:\n%s\nwant:\n%s", got, tt.want)
			}
		})
	}
}

func randText(r *rand.Rand) string {
	var sb strings.Builder
	for range r.Intn(30) {
		sb.WriteByte(byte('a' + r.Intn(4)))
		sb.WriteByte('\n')
	}
	return sb.String()
}

// TestEditsRoundTrip checks that the edit script is consistent with both inputs.
func TestEditsRoundTrip(t *testing.T) {
	r := rand.New(rand.NewSource(1))
	for range 2000 {
		a, b := Lines(randText(r)), Lines(randText(r))
		var gotA, gotB []string
		for _, op := range Edits(a, b) {
			if op.Kind != Insert {
				gotA = append(gotA, op.Line)
			}
			if op.Kind != Delete {
				gotB = append(gotB, op.Line)
			}
		}
		if strings.Join(gotA, "") != strings.Join(a, "") || strings.Join(gotB, "") != strings.Join(b, "") {
			t.Fatalf("edit script does not reproduce inputs\na=%q\nb=%q", a, b)
		}
	}
}

// TestPatchCompatible checks that our output applies cleanly with patch(1).
func TestPatchCompatible(t *testing.T) {
	if _, err := exec.LookPath("patch"); err != nil {
		t.Skip("patch not installed")
	}
	r := rand.New(rand.NewSource(2))
	dir := t.TempDir()
	file := filepath.Join(dir, "f")
	for range 200 {
		a, b := randText(r), randText(r)
		d := Unified("f", "f", a, b, r.Intn(4))
		if d == "" {
			continue
		}
		if err := os.WriteFile(file, []byte(a), 0o644); err != nil {
			t.Fatal(err)
		}
		cmd := exec.Command("patch", "-s", "-F0", file)
		cmd.Stdin = strings.NewReader(d)
		if out, err := cmd.CombinedOutput(); err != nil {
			t.Fatalf("patch failed: %v\n%s\ndiff:\n%s", err, out, d)
		}
		got, _ := os.ReadFile(file)
		if string(got) != b {
			t.Fatalf("patched result mismatch\na=%q\nb=%q\ndiff:\n%s", a, b, d)
		}
	}
}

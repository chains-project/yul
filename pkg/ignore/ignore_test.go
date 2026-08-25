package ignore

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadMissingFile(t *testing.T) {
	set := Load(t.TempDir())
	if len(set) != 0 {
		t.Fatalf("Load on a dir with no %s = %v, want empty", Filename, set)
	}
}

func TestLoadEmptyDir(t *testing.T) {
	set := Load("")
	if len(set) != 0 {
		t.Fatalf("Load(\"\") = %v, want empty", set)
	}
}

func TestLoadParsesEntriesAndSkipsCommentsAndBlanks(t *testing.T) {
	dir := t.TempDir()
	content := "# kept for compatibility with our internal fork\n" +
		"pkg:npm/lodash@4.17.20\n" +
		"\n" +
		"  pkg:maven/com.squareup.okhttp3/okhttp@4.9.0  \n"
	if err := os.WriteFile(filepath.Join(dir, Filename), []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}

	set := Load(dir)
	if !set.Contains("pkg:npm/lodash", "4.17.20") {
		t.Error("expected pkg:npm/lodash@4.17.20 to be ignored")
	}
	if !set.Contains("pkg:maven/com.squareup.okhttp3/okhttp", "4.9.0") {
		t.Error("expected the trimmed maven entry to be ignored")
	}
	if set.Contains("pkg:npm/lodash", "4.17.21") {
		t.Error("a different version of an ignored package should not be ignored")
	}
	if len(set) != 2 {
		t.Fatalf("len(set) = %d, want 2 (comment and blank line should not count)", len(set))
	}
}

func TestSetContainsEmptyInputs(t *testing.T) {
	set := Set{"pkg:npm/lodash@4.17.20": true}
	if set.Contains("", "4.17.20") {
		t.Error("Contains with empty purl should be false")
	}
	if set.Contains("pkg:npm/lodash", "") {
		t.Error("Contains with empty version should be false")
	}
}

package diff

import (
	"strings"
	"testing"
)

func TestUnifiedIdentical(t *testing.T) {
	if got := Unified("a\nb\nc\n", "a\nb\nc\n"); got != "" {
		t.Fatalf("expected empty diff, got:\n%s", got)
	}
	if got := Unified("", ""); got != "" {
		t.Fatalf("expected empty diff for empty inputs, got:\n%s", got)
	}
}

func TestUnifiedReplace(t *testing.T) {
	got := Unified("a\nb\nc\n", "a\nx\nc\n")
	want := strings.Join([]string{
		"--- a",
		"+++ b",
		"@@ -1,3 +1,3 @@",
		" a",
		"-b",
		"+x",
		" c",
		"",
	}, "\n")
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedInsertAtStart(t *testing.T) {
	got := Unified("b\nc\n", "a\nb\nc\n")
	want := strings.Join([]string{
		"--- a",
		"+++ b",
		"@@ -1,2 +1,3 @@",
		"+a",
		" b",
		" c",
		"",
	}, "\n")
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedDeleteAtStart(t *testing.T) {
	got := Unified("a\nb\nc\n", "b\nc\n")
	want := strings.Join([]string{
		"--- a",
		"+++ b",
		"@@ -1,3 +1,2 @@",
		"-a",
		" b",
		" c",
		"",
	}, "\n")
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedSeparateHunksWithZeroContext(t *testing.T) {
	old := "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n"
	neu := "1\nX\n3\n4\n5\n6\n7\n8\nY\n10\n"
	got := UnifiedContext(old, neu, 0)
	want := strings.Join([]string{
		"--- a",
		"+++ b",
		"@@ -2 +2 @@",
		"-2",
		"+X",
		"@@ -9 +9 @@",
		"-9",
		"+Y",
		"",
	}, "\n")
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedClampsNegativeContext(t *testing.T) {
	got := UnifiedContext("a\nb\n", "a\nc\n", -5)
	want := strings.Join([]string{
		"--- a",
		"+++ b",
		"@@ -2 +2 @@",
		"-b",
		"+c",
		"",
	}, "\n")
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedNoNewlineMarkers(t *testing.T) {
	got := Unified("a\nb", "a\nc")
	want := strings.Join([]string{
		"--- a",
		"+++ b",
		"@@ -1,2 +1,2 @@",
		" a",
		"-b",
		"\\ No newline at end of file",
		"+c",
		"\\ No newline at end of file",
		"",
	}, "\n")
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedContextMarkerOnly(t *testing.T) {
	got := Unified("a", "a\nb\n")
	want := strings.Join([]string{
		"--- a",
		"+++ b",
		"@@ -1 +1,2 @@",
		" a",
		"\\ No newline at end of file",
		"+b",
		"",
	}, "\n")
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedLabelsCanBeOmitted(t *testing.T) {
	got := UnifiedLabels("a\n", "b\n", "", "", 3)
	if strings.Contains(got, "---") || strings.Contains(got, "+++") {
		t.Fatalf("expected headers to be omitted, got:\n%s", got)
	}
	if !strings.HasPrefix(got, "@@") {
		t.Fatalf("expected hunk header first, got:\n%s", got)
	}
}

func TestMyersReconstructsNewText(t *testing.T) {
	cases := []struct {
		a, b []string
	}{
		{nil, nil},
		{nil, []string{"x"}},
		{[]string{"x"}, nil},
		{[]string{"a", "b", "c"}, []string{"a", "b", "c"}},
		{[]string{"a", "b", "c"}, []string{"a", "x", "c"}},
		{[]string{"the", "quick", "brown", "fox"}, []string{"the", "slow", "red", "fox"}},
		{[]string{"one", "two", "three", "four"}, []string{"zero", "one", "three", "four", "five"}},
		{[]string{"a", "a", "a"}, []string{"a", "b", "a"}},
	}

	for _, tc := range cases {
		edits := Myers(tc.a, tc.b)
		var got []string
		for _, e := range edits {
			if e.Op == Equal || e.Op == Insert {
				got = append(got, e.Text)
			}
		}
		if strings.Join(got, "\x00") != strings.Join(tc.b, "\x00") {
			t.Fatalf("Myers(%v, %v) reconstructed %v", tc.a, tc.b, got)
		}
	}
}

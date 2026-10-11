package difftool

import (
	"strconv"
	"strings"
	"testing"
)

func TestSplitLines(t *testing.T) {
	tests := []struct {
		in   string
		want []string
	}{
		{"", nil},
		{"a", []string{"a"}},
		{"a\n", []string{"a"}},
		{"a\nb\n", []string{"a", "b"}},
		{"a\nb", []string{"a", "b"}},
		{"\n", []string{""}},
		{"a\n\n", []string{"a", ""}},
	}
	for _, tt := range tests {
		got := SplitLines(tt.in)
		if len(got) != len(tt.want) {
			t.Fatalf("SplitLines(%q) = %q, want %q", tt.in, got, tt.want)
		}
		for i := range got {
			if got[i] != tt.want[i] {
				t.Fatalf("SplitLines(%q) = %q, want %q", tt.in, got, tt.want)
			}
		}
	}
}

func TestUnified(t *testing.T) {
	tests := []struct {
		name string
		a, b string
		want string
	}{
		{
			name: "identical",
			a:    "one\ntwo\nthree\n",
			b:    "one\ntwo\nthree\n",
			want: "",
		},
		{
			name: "single line change",
			a:    "one\ntwo\nthree\n",
			b:    "one\nTWO\nthree\n",
			want: "--- a\n+++ b\n@@ -1,3 +1,3 @@\n one\n-two\n+TWO\n three\n",
		},
		{
			name: "insertion in the middle",
			a:    "one\nthree\n",
			b:    "one\ntwo\nthree\n",
			want: "--- a\n+++ b\n@@ -1,2 +1,3 @@\n one\n+two\n three\n",
		},
		{
			name: "deletion at the start",
			a:    "zero\none\ntwo\n",
			b:    "one\ntwo\n",
			want: "--- a\n+++ b\n@@ -1,3 +1,2 @@\n-zero\n one\n two\n",
		},
		{
			name: "insertion into an empty file",
			a:    "",
			b:    "one\n",
			want: "--- a\n+++ b\n@@ -0,0 +1 @@\n+one\n",
		},
		{
			name: "deletion of everything",
			a:    "one\n",
			b:    "",
			want: "--- a\n+++ b\n@@ -1 +0,0 @@\n-one\n",
		},
		{
			name: "replacement at the beginning of an empty file",
			a:    "",
			b:    "one\ntwo\nthree\n",
			want: "--- a\n+++ b\n@@ -0,0 +1,3 @@\n+one\n+two\n+three\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := UnifiedText(tt.a, tt.b, Options{}); got != tt.want {
				t.Errorf("UnifiedText mismatch\n--- got ---\n%s\n--- want ---\n%s", got, tt.want)
			}
		})
	}
}

func TestUnifiedContext(t *testing.T) {
	var a, b []string
	for i := 1; i <= 20; i++ {
		a = append(a, string(rune('a'+i-1)))
		b = append(b, string(rune('a'+i-1)))
	}
	a[9] = "CHANGED" // line 10
	b[9] = "changed"

	got := Unified(a, b, Options{Context: 3})
	want := "--- a\n+++ b\n" +
		"@@ -7,7 +7,7 @@\n" +
		" g\n h\n i\n" +
		"-CHANGED\n+changed\n" +
		" k\n l\n m\n"
	if got != want {
		t.Errorf("context mismatch\n--- got ---\n%s\n--- want ---\n%s", got, want)
	}
}

func TestUnifiedMergesNearbyChanges(t *testing.T) {
	var a, b []string
	for i := 1; i <= 12; i++ {
		a = append(a, string(rune('a'+i-1)))
		b = append(b, string(rune('a'+i-1)))
	}
	a[2] = "X" // line 3
	b[2] = "x"
	a[5] = "Y" // line 6, only 2 lines after the first change
	b[5] = "y"

	got := Unified(a, b, Options{Context: 3})
	if !strings.Contains(got, "@@ -1,9 +1,9 @@") {
		t.Errorf("expected a single merged hunk, got:\n%s", got)
	}
	if strings.Count(got, "@@") != 2 { // one header, two @@ markers
		t.Errorf("expected exactly one hunk header, got:\n%s", got)
	}
}

func TestUnifiedSplitsDistantChanges(t *testing.T) {
	var a, b []string
	for i := 1; i <= 40; i++ {
		a = append(a, string(rune('a'+i-1)))
		b = append(b, string(rune('a'+i-1)))
	}
	a[1] = "X" // line 2
	b[1] = "x"
	a[38] = "Y" // line 39
	b[38] = "y"

	got := Unified(a, b, Options{Context: 3})
	if n := strings.Count(got, "@@ -"); n != 2 {
		t.Errorf("expected two hunks, got %d:\n%s", n, got)
	}
}

func FuzzUnifiedRoundTrip(f *testing.F) {
	f.Add("a\nb\nc\n", "a\nB\nc\n")
	f.Add("", "")
	f.Add("x\n", "")
	f.Add("", "y\n")
	f.Add("same\nsame\n", "same\n")
	f.Fuzz(func(t *testing.T, a, b string) {
		al, bl := SplitLines(a), SplitLines(b)
		diff := Unified(al, bl, Options{})
		if equalLines(al, bl) {
			if diff != "" {
				t.Fatalf("identical input produced a diff:\n%s", diff)
			}
			return
		}
		if got := applyDiff(al, diff); !equalLines(got, bl) {
			t.Fatalf("diff did not reconstruct b\n a=%q\n b=%q\ndiff:\n%s\ngot=%q", a, b, diff, got)
		}
	})
}

func equalLines(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

func applyDiff(orig []string, diff string) []string {
	lines := strings.Split(strings.TrimSuffix(diff, "\n"), "\n")
	if len(lines) < 2 {
		return orig
	}
	out := []string{}
	pos := 0
	for i := 2; i < len(lines); {
		if !strings.HasPrefix(lines[i], "@@") {
			i++
			continue
		}
		parts := strings.Fields(strings.TrimSuffix(strings.TrimPrefix(lines[i], "@@ "), " @@"))
		aStart, aCount := parseRange(strings.TrimPrefix(parts[0], "-"))
		aStart0 := aStart
		if aCount > 0 {
			aStart0 = aStart - 1
		}
		out = append(out, orig[pos:aStart0]...)
		pos = aStart0
		for i++; i < len(lines) && !strings.HasPrefix(lines[i], "@@"); i++ {
			switch lines[i][0] {
			case ' ':
				out = append(out, lines[i][1:])
				pos++
			case '-':
				pos++
			case '+':
				out = append(out, lines[i][1:])
			}
		}
	}
	return append(out, orig[pos:]...)
}

func parseRange(s string) (start, count int) {
	if i := strings.IndexByte(s, ','); i >= 0 {
		start, _ = strconv.Atoi(s[:i])
		count, _ = strconv.Atoi(s[i+1:])
		return start, count
	}
	start, _ = strconv.Atoi(s)
	return start, 1
}

func TestUnifiedCustomNames(t *testing.T) {
	got := UnifiedText("a\n", "b\n", Options{FromName: "old.txt", ToName: "new.txt"})
	want := "--- old.txt\n+++ new.txt\n@@ -1 +1 @@\n-a\n+b\n"
	if got != want {
		t.Errorf("got:\n%s\nwant:\n%s", got, want)
	}
}

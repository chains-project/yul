package diff

import (
	"strings"
	"testing"
)

func TestUnifiedIdentical(t *testing.T) {
	if got := Unified("a\nb\nc\n", "a\nb\nc\n"); got != "" {
		t.Fatalf("expected empty diff, got:\n%s", got)
	}
}

func TestUnifiedReplaceLine(t *testing.T) {
	got := UnifiedNamed("old.txt", "new.txt", "hello\n", "world\n")
	want := strings.Join([]string{
		"--- old.txt",
		"+++ new.txt",
		"@@ -1 +1 @@",
		"-hello",
		"+world",
		"",
	}, "\n")
	if got != want {
		t.Fatalf("got:\n%q\nwant:\n%q", got, want)
	}
}

func TestUnifiedInsertIntoEmpty(t *testing.T) {
	got := Unified("", "x\ny\n")
	want := strings.Join([]string{
		"--- a",
		"+++ b",
		"@@ -0,0 +1,2 @@",
		"+x",
		"+y",
		"",
	}, "\n")
	if got != want {
		t.Fatalf("got:\n%q\nwant:\n%q", got, want)
	}
}

func TestUnifiedDeleteToEmpty(t *testing.T) {
	got := Unified("x\ny\n", "")
	want := strings.Join([]string{
		"--- a",
		"+++ b",
		"@@ -1,2 +0,0 @@",
		"-x",
		"-y",
		"",
	}, "\n")
	if got != want {
		t.Fatalf("got:\n%q\nwant:\n%q", got, want)
	}
}

func TestUnifiedAppendToFile(t *testing.T) {
	a := "l1\nl2\nl3\nl4\nl5\n"
	b := "l1\nl2\nl3\nl4\nl5\nl6\n"
	got := Unified(a, b)
	want := strings.Join([]string{
		"--- a",
		"+++ b",
		"@@ -3,3 +3,4 @@",
		" l3",
		" l4",
		" l5",
		"+l6",
		"",
	}, "\n")
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedMultipleHunks(t *testing.T) {
	var a, b []string
	for i := 1; i <= 20; i++ {
		a = append(a, "line"+itoa(i))
	}
	b = append(b, a...)
	b[1] = "changed2"
	b[17] = "changed18"

	got := Unified(strings.Join(a, "\n")+"\n", strings.Join(b, "\n")+"\n")
	want := strings.Join([]string{
		"--- a",
		"+++ b",
		"@@ -1,5 +1,5 @@",
		" line1",
		"-line2",
		"+changed2",
		" line3",
		" line4",
		" line5",
		"@@ -15,6 +15,6 @@",
		" line15",
		" line16",
		" line17",
		"-line18",
		"+changed18",
		" line19",
		" line20",
		"",
	}, "\n")
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnifiedNoTrailingNewline(t *testing.T) {
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
		t.Fatalf("got:\n%q\nwant:\n%q", got, want)
	}
}

func TestUnifiedContextZero(t *testing.T) {
	got := Config{Context: -1}.Unified("a\nb\n", "a\nc\n")
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

// TestComputeOpsRoundTrip verifies the edit script reconstructs the new text
// from the old text for a range of inputs.
func TestComputeOpsRoundTrip(t *testing.T) {
	cases := [][2][]string{
		{nil, nil},
		{{"a"}, nil},
		{nil, {"a"}},
		{{"a", "b", "c"}, {"a", "c"}},
		{{"a", "c"}, {"a", "b", "c"}},
		{{"a", "b"}, {"c", "d"}},
		{{"a", "b", "c", "d"}, {"a", "x", "c", "y"}},
	}
	for _, tc := range cases {
		ops := computeOps(tc[0], tc[1])
		var rebuilt, old []string
		for _, op := range ops {
			switch op.Kind {
			case Equal:
				rebuilt = append(rebuilt, op.Text)
				old = append(old, op.Text)
			case Delete:
				old = append(old, op.Text)
			case Insert:
				rebuilt = append(rebuilt, op.Text)
			}
		}
		if !equalSlices(rebuilt, tc[1]) {
			t.Errorf("rebuilt %q, want %q", rebuilt, tc[1])
		}
		if !equalSlices(old, tc[0]) {
			t.Errorf("consumed old %q, want %q", old, tc[0])
		}
	}
}

func equalSlices(a, b []string) bool {
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

func itoa(n int) string {
	if n == 0 {
		return "0"
	}
	var buf [20]byte
	i := len(buf)
	for n > 0 {
		i--
		buf[i] = byte('0' + n%10)
		n /= 10
	}
	return string(buf[i:])
}

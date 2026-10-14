package textdiff

import (
	"fmt"
	"testing"
)

func TestUnifiedEqual(t *testing.T) {
	if d := Unified("a", "b", "same\n", "same\n"); d != "" {
		t.Fatalf("expected empty diff, got:\n%s", d)
	}
}

func TestUnified(t *testing.T) {
	want := "one\ntwo\nthree\n"
	got := "one\n2\nthree\n"
	exp := `--- a
+++ b
@@ -1,3 +1,3 @@
 one
-two
+2
 three
`
	if d := Unified("a", "b", want, got); d != exp {
		t.Errorf("Unified:\n%s\nwant:\n%s", d, exp)
	}
}

func TestUnifiedNoTrailingNewline(t *testing.T) {
	d := Unified("a", "b", "x", "y")
	exp := `--- a
+++ b
@@ -1 +1 @@
-x
\ No newline at end of file
+y
\ No newline at end of file
`
	if d != exp {
		t.Errorf("Unified:\n%s\nwant:\n%s", d, exp)
	}
}

func TestUnifiedContext(t *testing.T) {
	want := "1\n2\n3\n4\n5\n"
	got := "1\n2\nX\n4\n5\n"
	d, err := UnifiedContext("a", "b", want, got, 0)
	if err != nil {
		t.Fatal(err)
	}
	exp := "--- a\n+++ b\n@@ -3 +3 @@\n-3\n+X\n"
	if d != exp {
		t.Errorf("UnifiedContext:\n%s\nwant:\n%s", d, exp)
	}
	if _, err := UnifiedContext("a", "b", want, got, -1); err == nil {
		t.Error("expected error for negative context")
	}
}

type fakeTB struct{ msgs []string }

func (f *fakeTB) Helper() {}
func (f *fakeTB) Errorf(format string, args ...any) {
	f.msgs = append(f.msgs, fmt.Sprintf(format, args...))
}

func TestCheck(t *testing.T) {
	var f fakeTB
	if !Check(&f, "a\n", "a\n") || len(f.msgs) != 0 {
		t.Errorf("Check on equal input reported %v", f.msgs)
	}
	if Check(&f, "a\n", "b\n") || len(f.msgs) != 1 {
		t.Errorf("Check on different input: msgs=%v", f.msgs)
	}
}

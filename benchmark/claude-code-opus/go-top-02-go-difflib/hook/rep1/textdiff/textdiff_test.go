package textdiff

import "testing"

func TestUnifiedIdentical(t *testing.T) {
	if d := Unified("want", "got", "a\nb\n", "a\nb\n"); d != "" {
		t.Errorf("expected empty diff, got:\n%s", d)
	}
}

func TestUnified(t *testing.T) {
	want := "a\nb\nc\n"
	got := "a\nB\nc\n"
	expected := `--- want
+++ got
@@ -1,3 +1,3 @@
 a
-b
+B
 c
`
	if d := Unified("want", "got", want, got); d != expected {
		t.Errorf("unexpected diff:\n%s\nexpected:\n%s", d, expected)
	}
}

func TestUnifiedContext(t *testing.T) {
	want := "1\n2\n3\n4\n5\n"
	got := "1\n2\nX\n4\n5\n"
	expected := `--- want
+++ got
@@ -3 +3 @@
-3
+X
`
	d, err := UnifiedContext("want", "got", want, got, 0)
	if err != nil {
		t.Fatal(err)
	}
	if d != expected {
		t.Errorf("unexpected diff:\n%s\nexpected:\n%s", d, expected)
	}
	if _, err := UnifiedContext("want", "got", want, got, -1); err == nil {
		t.Error("expected error for negative context")
	}
}

package unified

import "testing"

func TestDiffIdentical(t *testing.T) {
	if got := Diff("a\nb\n", "a\nb\n"); got != "" {
		t.Fatalf("expected empty diff, got:\n%s", got)
	}
}

func TestDiffSimple(t *testing.T) {
	old := "one\ntwo\nthree\n"
	new := "one\nthree\nfour\n"
	want := "--- old\n+++ new\n" +
		"@@ -1,3 +1,3 @@\n" +
		" one\n" +
		"-two\n" +
		" three\n" +
		"+four\n"
	if got := Diff(old, new); got != want {
		t.Fatalf("unexpected diff:\ngot:\n%s\nwant:\n%s", got, want)
	}
}

func TestDiffNamed(t *testing.T) {
	got := DiffNamed("a\n", "b\n", "before.txt", "after.txt", DefaultContext)
	want := "--- before.txt\n+++ after.txt\n@@ -1 +1 @@\n-a\n+b\n"
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestDiffNoNewlineAtEnd(t *testing.T) {
	got := Diff("a\nb", "a\nb\n")
	want := "--- old\n+++ new\n" +
		"@@ -1,2 +1,2 @@\n" +
		" a\n" +
		"-b\n" +
		"\\ No newline at end of file\n" +
		"+b\n"
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestDiffInsertIntoEmpty(t *testing.T) {
	got := Diff("", "hello\n")
	want := "--- old\n+++ new\n@@ -0,0 +1 @@\n+hello\n"
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestDiffDeleteToEmpty(t *testing.T) {
	got := Diff("hello\n", "")
	want := "--- old\n+++ new\n@@ -1 +0,0 @@\n-hello\n"
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestDiffMultipleHunks(t *testing.T) {
	old := "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n"
	new := "1\nX\n3\n4\n5\n6\n7\n8\nY\n10\n"
	got := DiffContext(old, new, 1)
	want := "--- old\n+++ new\n" +
		"@@ -1,3 +1,3 @@\n" +
		" 1\n" +
		"-2\n" +
		"+X\n" +
		" 3\n" +
		"@@ -8,3 +8,3 @@\n" +
		" 8\n" +
		"-9\n" +
		"+Y\n" +
		" 10\n"
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestDiffContextZero(t *testing.T) {
	got := DiffContext("a\nb\nc\n", "a\nB\nc\n", 0)
	want := "--- old\n+++ new\n@@ -2 +2 @@\n-b\n+B\n"
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestDiffHandlesCRLFAndTabs(t *testing.T) {
	got := DiffContext("a\tb\r\n", "a\tc\r\n", DefaultContext)
	want := "--- old\n+++ new\n@@ -1 +1 @@\n-a\tb\r\n+a\tc\r\n"
	if got != want {
		t.Fatalf("got:\n%q\nwant:\n%q", got, want)
	}
}

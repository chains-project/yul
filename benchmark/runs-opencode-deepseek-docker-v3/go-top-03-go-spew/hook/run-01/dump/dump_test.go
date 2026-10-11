package dump

import (
	"bytes"
	"strings"
	"testing"
)

type node struct {
	Name  string
	Child *node
	Tags  map[string]int
}

func TestSdumpNestedValue(t *testing.T) {
	root := &node{Name: "root", Tags: map[string]int{"b": 2, "a": 1}}
	root.Child = &node{Name: "leaf"}

	got := Sdump(root)

	for _, want := range []string{"(*dump.node)", `"root"`, `"leaf"`, `"a"`, `"b"`} {
		if !strings.Contains(got, want) {
			t.Fatalf("Sdump() missing %q in:\n%s", want, got)
		}
	}
	if strings.Contains(got, "0x") {
		t.Fatalf("pointer addresses should be suppressed, got:\n%s", got)
	}
}

func TestSortKeysIsDeterministic(t *testing.T) {
	m := map[string]int{"c": 3, "a": 1, "b": 2}

	got := Sdump(m)

	if strings.Index(got, "a: 1") > strings.Index(got, "b: 2") {
		t.Fatalf("map keys are not sorted:\n%s", got)
	}
}

func TestDepthStopsRecursion(t *testing.T) {
	cur := &node{Name: "0"}
	for i := 1; i < 6; i++ {
		cur = &node{Name: "x", Child: cur}
	}

	got := Depth(2).Sdump(cur)

	if !strings.Contains(got, "<max depth reached>") {
		t.Fatalf("expected elision marker when depth is exceeded, got:\n%s", got)
	}
}

func TestCycleIsAnnotated(t *testing.T) {
	n := &node{Name: "self"}
	n.Child = n

	got := Sdump(n)

	if !strings.Contains(got, "<already shown>") {
		t.Fatalf("expected cycle annotation, got:\n%s", got)
	}
}

func TestFdumpWritesToWriter(t *testing.T) {
	var buf bytes.Buffer

	Fdump(&buf, map[string]string{"k": "v"})

	if buf.Len() == 0 {
		t.Fatal("Fdump wrote nothing")
	}
}

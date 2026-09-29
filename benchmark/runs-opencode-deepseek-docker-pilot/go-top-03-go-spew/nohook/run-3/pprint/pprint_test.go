package pprint

import (
	"bytes"
	"strings"
	"testing"
)

type secret struct {
	Exported int
	hidden   string
}

type node struct {
	Name string
	Next *node
}

func TestDumpIncludesUnexportedFields(t *testing.T) {
	out := Sdump(secret{Exported: 1, hidden: "shh"})
	for _, want := range []string{"secret", "Exported", "1", "hidden", "shh"} {
		if !strings.Contains(out, want) {
			t.Errorf("Sdump output missing %q:\n%s", want, out)
		}
	}
}

func TestDumpTerminatesOnCycles(t *testing.T) {
	a := &node{Name: "a"}
	a.Next = a

	out := Sdump(a)
	if !strings.Contains(out, "Next") {
		t.Fatalf("cycle was not rendered:\n%s", out)
	}
	if len(out) > 4096 {
		t.Fatalf("cycle produced unbounded output (%d bytes)", len(out))
	}
}

func TestDumpIsDeterministicForMaps(t *testing.T) {
	m := map[string]int{"b": 2, "a": 1, "c": 3}
	first := Sdump(m)
	for i := 0; i < 20; i++ {
		if got := Sdump(m); got != first {
			t.Fatalf("map output not deterministic:\n%s\nvs\n%s", first, got)
		}
	}
}

func TestDumpExpandsInterfacesAndPointers(t *testing.T) {
	var v interface{} = []int{1, 2, 3}
	out := Sdump(v)
	if !strings.Contains(out, "[]int") {
		t.Errorf("interface was not expanded to its dynamic type:\n%s", out)
	}
}

func TestFdumpWritesToWriter(t *testing.T) {
	var buf bytes.Buffer
	Fdump(&buf, 42)
	if !strings.Contains(buf.String(), "42") {
		t.Errorf("Fdump wrote %q", buf.String())
	}
}

func TestNewIndent(t *testing.T) {
	var buf bytes.Buffer
	New("\t").Fdump(&buf, secret{Exported: 7, hidden: "x"})
	if !strings.Contains(buf.String(), "\t") {
		t.Errorf("custom indent was not applied:\n%s", buf.String())
	}
}

package godump

import (
	"bytes"
	"strings"
	"testing"
)

type address struct {
	Street string
	City   string
}

type person struct {
	Name    string
	Age     int
	Tags    []string
	Meta    map[string]any
	Address *address
	Friend  *person
}

func samplePerson() *person {
	return &person{
		Name: "Ada",
		Age:  36,
		Tags: []string{"math", "engineer"},
		Meta: map[string]any{
			"active": true,
			"score":  9.5,
		},
		Address: &address{Street: "1 Analytical Way", City: "London"},
	}
}

func TestSdumpNestedStructures(t *testing.T) {
	out := Sdump(samplePerson())
	for _, want := range []string{"(*godump.person)", "Name:", "Ada", "Tags:", "math", "Meta:", "active", "score", "(*godump.address)", "London"} {
		if !strings.Contains(out, want) {
			t.Fatalf("Sdump output missing %q:\n%s", want, out)
		}
	}
}

func TestSdumpVariadic(t *testing.T) {
	out := Sdump("first", 2, []int{3, 4})
	for _, want := range []string{"first", "(int) 2", "[]int", "3", "4"} {
		if !strings.Contains(out, want) {
			t.Fatalf("Sdump output missing %q:\n%s", want, out)
		}
	}
}

func TestCycleDetection(t *testing.T) {
	n := &person{Name: "loop"}
	n.Friend = n
	out := Sdump(n)
	if !strings.Contains(out, "<already shown>") {
		t.Fatalf("expected cycle marker, got:\n%s", out)
	}
}

func TestMaxDepth(t *testing.T) {
	d := New(WithMaxDepth(1))
	out := d.Sdump(samplePerson())
	if !strings.Contains(out, "Name:") {
		t.Fatalf("depth 1 should still show top-level fields:\n%s", out)
	}
	if strings.Contains(out, "London") {
		t.Fatalf("depth 1 should not descend into nested address:\n%s", out)
	}
}

func TestPointerAddresses(t *testing.T) {
	withAddrs := New(WithPointerAddresses(true)).Sdump(&address{City: "X"})
	if !strings.Contains(withAddrs, "0x") {
		t.Fatalf("expected pointer address:\n%s", withAddrs)
	}
	without := New(WithPointerAddresses(false)).Sdump(&address{City: "X"})
	if strings.Contains(without, "0x") {
		t.Fatalf("did not expect pointer address:\n%s", without)
	}
}

func TestFdump(t *testing.T) {
	var buf bytes.Buffer
	Fdump(&buf, samplePerson())
	if !strings.Contains(buf.String(), "Ada") {
		t.Fatalf("Fdump output missing value:\n%s", buf.String())
	}
}

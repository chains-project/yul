package godump

import (
	"strings"
	"testing"
)

type point struct {
	X, Y int
}

type config struct {
	Name  string
	Ports []int
	Any   any
}

type node struct {
	Value int
	Next  *node
}

func TestScalars(t *testing.T) {
	cases := []struct {
		in   any
		want string
	}{
		{42, "42"},
		{-7, "-7"},
		{uint8(255), "255"},
		{3.5, "3.5"},
		{"hi\n", `"hi\n"`},
		{true, "true"},
		{nil, "<invalid>"},
	}
	for _, tc := range cases {
		if got := Sdump(tc.in); got != tc.want {
			t.Errorf("Sdump(%#v) = %q, want %q", tc.in, got, tc.want)
		}
	}
}

func TestStructFormatting(t *testing.T) {
	got := Sdump(point{X: 1, Y: 2})
	want := "godump.point{\n    X: 1,\n    Y: 2,\n}"
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestNestedSequenceInline(t *testing.T) {
	got := Sdump(config{Name: "svc", Ports: []int{80, 443}})
	want := "godump.config{\n    Name: \"svc\",\n    Ports: []int{80, 443},\n    Any: nil,\n}"
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestInterfaceKeepsDynamicType(t *testing.T) {
	if got := Sdump([]any{5}); got != "[]interface {}{int(5)}" {
		t.Fatalf("got %q, want %q", got, "[]interface {}{int(5)}")
	}
}

func TestTypedNil(t *testing.T) {
	var p *int
	if got := Sdump(p); got != "*int(nil)" {
		t.Fatalf("got %q, want %q", got, "*int(nil)")
	}
}

func TestMapOrderIsDeterministic(t *testing.T) {
	m := map[string]int{"c": 3, "a": 1, "b": 2}
	want := `map[string]int{"a": 1, "b": 2, "c": 3}`
	if got := Sdump(m); got != want {
		t.Fatalf("got %q, want %q", got, want)
	}
}

func TestPointerCycle(t *testing.T) {
	a := &node{Value: 1}
	a.Next = a

	got := Sdump(a)
	if !strings.Contains(got, "<cycle: *godump.node>") {
		t.Fatalf("expected cycle marker, got:\n%s", got)
	}
}

func TestMapCycle(t *testing.T) {
	m := map[string]any{}
	m["self"] = m

	got := Sdump(m)
	if !strings.Contains(got, "<cycle: map[string]interface {}>") {
		t.Fatalf("expected cycle marker, got:\n%s", got)
	}
}

func TestSliceSelfReference(t *testing.T) {
	s := []any{nil}
	s[0] = s

	got := Sdump(s)
	if !strings.Contains(got, "<cycle") {
		t.Fatalf("expected cycle marker, got:\n%s", got)
	}
}

func TestUnexportedFields(t *testing.T) {
	type hidden struct {
		Public  int
		private string
	}
	got := Sdump(hidden{Public: 1, private: "shh"})
	if !strings.Contains(got, "private: \"shh\"") {
		t.Fatalf("expected unexported field to be rendered, got:\n%s", got)
	}
}

func TestMaxDepth(t *testing.T) {
	a := &node{Value: 1, Next: &node{Value: 2}}
	p := &Printer{MaxDepth: 1}
	got := p.Sdump(a)
	if !strings.Contains(got, "...") {
		t.Fatalf("expected truncation marker, got:\n%s", got)
	}
}

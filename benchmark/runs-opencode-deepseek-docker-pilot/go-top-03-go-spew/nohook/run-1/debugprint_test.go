package debugprint

import (
	"strings"
	"testing"
)

type point struct {
	X, Y int
}

type withHidden struct {
	Exported   string
	unexported int
	Nested     point
}

type node struct {
	Value int
	Next  *node
}

func TestPrimitives(t *testing.T) {
	cases := []struct {
		in   any
		want string
	}{
		{nil, "<nil>"},
		{true, "true"},
		{42, "42"},
		{-7, "-7"},
		{3.5, "3.5"},
		{"he\tllo", `"he\tllo"`},
	}
	for _, tc := range cases {
		if got := strings.TrimSpace(Sdump(tc.in)); got != tc.want {
			t.Errorf("Sdump(%#v) = %q, want %q", tc.in, got, tc.want)
		}
	}
}

func TestStructAndUnexportedFields(t *testing.T) {
	v := withHidden{Exported: "visible", unexported: 99, Nested: point{X: 1, Y: 2}}
	out := Sdump(v)
	for _, want := range []string{"Exported: \"visible\"", "unexported: 99", "X: 1", "Y: 2"} {
		if !strings.Contains(out, want) {
			t.Fatalf("output missing %q:\n%s", want, out)
		}
	}
}

func TestPointerIsDereferenced(t *testing.T) {
	n := 5
	out := strings.TrimSpace(Sdump(&n))
	if !strings.HasPrefix(out, "&") || !strings.Contains(out, "5") {
		t.Fatalf("expected dereferenced pointer, got %q", out)
	}
}

func TestNilPointerAndMap(t *testing.T) {
	var p *point
	if got := strings.TrimSpace(Sdump(p)); !strings.Contains(got, "nil") {
		t.Fatalf("nil pointer: got %q", got)
	}
	var m map[string]int
	if got := strings.TrimSpace(Sdump(m)); !strings.Contains(got, "nil") {
		t.Fatalf("nil map: got %q", got)
	}
}

func TestCycleDetection(t *testing.T) {
	a := &node{Value: 1}
	b := &node{Value: 2}
	a.Next = b
	b.Next = a
	out := Sdump(a)
	if !strings.Contains(out, "<cycle to ") {
		t.Fatalf("expected cycle marker, got:\n%s", out)
	}
}

func TestMapKeysSorted(t *testing.T) {
	m := map[string]int{"c": 3, "a": 1, "b": 2}
	out := Sdump(m)
	ia, ib, ic := strings.Index(out, `"a"`), strings.Index(out, `"b"`), strings.Index(out, `"c"`)
	if !(ia < ib && ib < ic) {
		t.Fatalf("map keys not sorted:\n%s", out)
	}
}

func TestMaxDepth(t *testing.T) {
	p := New(&Config{MaxDepth: 1})
	out := p.Sdump(map[string]any{"k": map[string]int{"x": 1}})
	if !strings.Contains(out, "...") {
		t.Fatalf("expected depth truncation, got:\n%s", out)
	}
}

func TestSlicesAndArrays(t *testing.T) {
	s := []int{1, 2, 3}
	out := Sdump(s)
	for _, want := range []string{"[]int[", "1,", "2,", "3"} {
		if !strings.Contains(out, want) {
			t.Fatalf("slice output missing %q:\n%s", want, out)
		}
	}
	if got := Sdump([2]string{"a", "b"}); !strings.Contains(got, "[2]string[") {
		t.Fatalf("array type missing: %q", got)
	}
}

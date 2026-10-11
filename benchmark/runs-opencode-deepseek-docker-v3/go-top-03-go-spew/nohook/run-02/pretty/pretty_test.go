package pretty

import (
	"strings"
	"testing"
)

type testNode struct {
	Name string
	Next *testNode
}

func TestBasic(t *testing.T) {
	cases := []struct {
		in   interface{}
		want string
	}{
		{nil, "<nil>"},
		{true, "true"},
		{42, "42"},
		{int8(-3), "-3"},
		{uint16(7), "7"},
		{3.5, "3.5"},
		{"hi", `"hi"`},
	}
	for _, c := range cases {
		if got := Sprint(c.in); got != c.want {
			t.Errorf("Sprint(%v) = %q, want %q", c.in, got, c.want)
		}
	}
}

func TestSliceAndMap(t *testing.T) {
	got := Sprint([]int{1, 2, 3})
	if !strings.Contains(got, "[]int{") || !strings.Contains(got, "1") {
		t.Fatalf("unexpected slice output: %s", got)
	}

	got = Sprint(map[string]int{"b": 2, "a": 1})
	ia := strings.Index(got, `"a"`)
	ib := strings.Index(got, `"b"`)
	if ia == -1 || ib == -1 || ia > ib {
		t.Fatalf("map keys not sorted: %s", got)
	}
}

func TestCycle(t *testing.T) {
	a := &testNode{Name: "a"}
	b := &testNode{Name: "b"}
	a.Next = b
	b.Next = a

	got := Sprint(a)
	if !strings.Contains(got, "<cycle>") {
		t.Fatalf("expected cycle marker, got: %s", got)
	}
}

func TestSharedNonCyclicPointer(t *testing.T) {
	shared := &testNode{Name: "shared"}
	root := struct {
		Left  *testNode
		Right *testNode
	}{Left: shared, Right: shared}

	got := Sprint(root)
	if strings.Contains(got, "<cycle>") {
		t.Fatalf("shared pointer was wrongly reported as a cycle: %s", got)
	}
	if strings.Count(got, `"shared"`) != 2 {
		t.Fatalf("expected shared value twice, got: %s", got)
	}
}

func TestUnexportedField(t *testing.T) {
	type hidden struct {
		Exported   int
		unexported string
	}
	got := Sprint(hidden{Exported: 1, unexported: "x"})
	if !strings.Contains(got, "unexported") || !strings.Contains(got, `"x"`) {
		t.Fatalf("unexpected output: %s", got)
	}
}

func TestNilPointer(t *testing.T) {
	var p *int
	got := Sprint(p)
	if !strings.Contains(got, "nil") {
		t.Fatalf("unexpected output: %s", got)
	}
}

func TestNilMapAndSlice(t *testing.T) {
	var m map[string]int
	if got := Sprint(m); !strings.Contains(got, "nil") {
		t.Fatalf("unexpected nil map output: %s", got)
	}
	var s []int
	if got := Sprint(s); !strings.Contains(got, "nil") {
		t.Fatalf("unexpected nil slice output: %s", got)
	}
}

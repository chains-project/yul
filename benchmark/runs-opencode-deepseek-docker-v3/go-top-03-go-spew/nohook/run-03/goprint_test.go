package goprint

import (
	"bytes"
	"strings"
	"testing"
)

type inner struct {
	N int
}

type outer struct {
	Name string
	In   inner
	P    *int
	priv int
}

type node struct {
	Name string
	Next *node
}

type link struct {
	V    int
	Next *link
}

func TestScalars(t *testing.T) {
	i := 7
	cases := []struct {
		name string
		in   any
		want string
	}{
		{"nil", nil, "<nil>"},
		{"bool", true, "true"},
		{"int", 42, "42"},
		{"negative", -3, "-3"},
		{"uint", uint(9), "9"},
		{"float", 3.5, "3.5"},
		{"complex", complex(1, 2), "(1+2i)"},
		{"complex neg", complex(1, -2), "(1-2i)"},
		{"string", "hi", `"hi"`},
		{"string escaping", "a\nb", `"a\nb"`},
		{"nil pointer", (*int)(nil), "(*int)(nil)"},
		{"int pointer", &i, "&7"},
		{"nil slice", []int(nil), "[]int(nil)"},
		{"nil map", map[string]int(nil), "map[string]int(nil)"},
		{"nil func", (func())(nil), "(func())(nil)"},
		{"nil chan", (chan int)(nil), "(chan int)(0x0)"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			if got := Sprint(tc.in); got != tc.want {
				t.Fatalf("Sprint(%v) =\n%q\nwant\n%q", tc.in, got, tc.want)
			}
		})
	}
}

func TestStruct(t *testing.T) {
	i := 7
	v := outer{Name: "hi", In: inner{N: 3}, P: &i, priv: 9}
	want := `goprint.outer{
	Name: "hi",
	In: goprint.inner{
		N: 3
	},
	P: &7,
	priv: 9
}`
	if got := Sprint(v); got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestMapSorted(t *testing.T) {
	want := `map[string]int{
	"a": 1,
	"b": 2,
	"c": 3
}`
	if got := Sprint(map[string]int{"c": 3, "a": 1, "b": 2}); got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestSliceAndArray(t *testing.T) {
	want := `[]int{
	1,
	2,
	3
}`
	if got := Sprint([]int{1, 2, 3}); got != want {
		t.Fatalf("slice got:\n%s\nwant:\n%s", got, want)
	}

	wantArray := `[2]string{
	"x",
	"y"
}`
	if got := Sprint([2]string{"x", "y"}); got != wantArray {
		t.Fatalf("array got:\n%s\nwant:\n%s", got, wantArray)
	}

	if got := Sprint([]int{}); got != "[]int{}" {
		t.Fatalf("empty slice got %q", got)
	}
}

func TestPointerCycle(t *testing.T) {
	a := &node{Name: "a"}
	b := &node{Name: "b", Next: a}
	a.Next = b

	want := `&goprint.node{
	Name: "a",
	Next: &goprint.node{
		Name: "b",
		Next: <cycle>
	}
}`
	if got := Sprint(a); got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestSliceCycle(t *testing.T) {
	s := make([]any, 1)
	s[0] = s

	want := `[]interface {}{
	<cycle>
}`
	if got := Sprint(s); got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestMapCycle(t *testing.T) {
	m := map[string]any{}
	m["self"] = m

	want := `map[string]interface {}{
	"self": <cycle>
}`
	if got := Sprint(m); got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestSharedNotCycle(t *testing.T) {
	i := 5
	v := struct {
		A *int
		B *int
	}{A: &i, B: &i}

	got := Sprint(v)
	if strings.Contains(got, "<cycle>") {
		t.Fatalf("shared acyclic pointer reported as cycle:\n%s", got)
	}
	if strings.Count(got, "&5") != 2 {
		t.Fatalf("expected both pointers printed fully, got:\n%s", got)
	}
}

func TestMaxDepth(t *testing.T) {
	l3 := &link{V: 3}
	l2 := &link{V: 2, Next: l3}
	l1 := &link{V: 1, Next: l2}

	want := `&goprint.link{
	V: 1,
	Next: &goprint.link{
		V: 2,
		Next: ...
	}
}`
	if got := SprintOpts(l1, Options{MaxDepth: 1}); got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestMaxItems(t *testing.T) {
	want := `[]int{
	1,
	2,
	... (2 more)
}`
	if got := SprintOpts([]int{1, 2, 3, 4}, Options{MaxItems: 2}); got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestCustomIndent(t *testing.T) {
	want := "[]int{\n  1,\n  2\n}"
	if got := SprintOpts([]int{1, 2}, Options{Indent: "  "}); got != want {
		t.Fatalf("got:\n%q\nwant:\n%q", got, want)
	}
}

func TestFprint(t *testing.T) {
	var buf bytes.Buffer
	if err := Fprint(&buf, map[string]int{"a": 1}); err != nil {
		t.Fatal(err)
	}
	if got, want := buf.String(), Sprint(map[string]int{"a": 1}); got != want {
		t.Fatalf("Fprint = %q, Sprint = %q", got, want)
	}
}

func TestNestedContainers(t *testing.T) {
	v := map[string][]inner{
		"b": {{N: 2}},
		"a": {{N: 1}, {N: 1}},
	}
	want := `map[string][]goprint.inner{
	"a": []goprint.inner{
		goprint.inner{
			N: 1
		},
		goprint.inner{
			N: 1
		}
	},
	"b": []goprint.inner{
		goprint.inner{
			N: 2
		}
	}
}`
	if got := Sprint(v); got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

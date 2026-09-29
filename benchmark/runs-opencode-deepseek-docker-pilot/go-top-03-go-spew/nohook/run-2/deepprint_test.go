package deepprint

import (
	"bytes"
	"math"
	"strings"
	"testing"
)

type point struct {
	X, Y int
}

type secret struct {
	Public  string
	private int
}

type node struct {
	Name string
	Next *node
}

func TestScalars(t *testing.T) {
	cases := []struct {
		name string
		in   any
		want string
	}{
		{"nil", nil, "<nil>"},
		{"bool", true, "(bool) true"},
		{"int", -42, "(int) -42"},
		{"uint", uint8(200), "(uint8) 200"},
		{"float", 1.5, "(float64) 1.5"},
		{"inf", math.Inf(1), "(float64) +Inf"},
		{"string", "hi\n", `(string) "hi\n"`},
		{"interface", any(7), "(int) 7"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			if got := Sdump(tc.in); got != tc.want {
				t.Fatalf("Sdump(%v) = %q, want %q", tc.in, got, tc.want)
			}
		})
	}
}

func TestStruct(t *testing.T) {
	got := Sdump(point{X: 1, Y: 2})
	want := "(deepprint.point) {\n" +
		"  X: (int) 1,\n" +
		"  Y: (int) 2,\n" +
		"}"
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestUnexportedFields(t *testing.T) {
	in := secret{Public: "a", private: 7}

	with := Sdump(in)
	if !strings.Contains(with, "private: (int) 7") {
		t.Fatalf("expected unexported field, got:\n%s", with)
	}

	p := New(Config{ShowTypes: true, ShowUnexported: false})
	without := p.Sdump(in)
	if strings.Contains(without, "private") {
		t.Fatalf("unexpected unexported field, got:\n%s", without)
	}
}

func TestPointerCycle(t *testing.T) {
	a := &node{Name: "a"}
	b := &node{Name: "b", Next: a}
	a.Next = b

	got := Sdump(a)
	if !strings.Contains(got, "<already shown>") {
		t.Fatalf("expected cycle marker, got:\n%s", got)
	}
	if strings.Count(got, `Name: (string) "a"`) != 1 {
		t.Fatalf("expected node a rendered once, got:\n%s", got)
	}
}

func TestMapDeterministic(t *testing.T) {
	m := map[string]int{"b": 2, "a": 1, "c": 3}
	got := Sdump(m)
	want := "(map[string]int) {\n" +
		"  (string) \"a\": (int) 1,\n" +
		"  (string) \"b\": (int) 2,\n" +
		"  (string) \"c\": (int) 3,\n" +
		"}"
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestSliceAndArray(t *testing.T) {
	slice := Sdump([]int{4, 5})
	wantSlice := "([]int) (len=2 cap=2) {\n  0: (int) 4,\n  1: (int) 5,\n}"
	if slice != wantSlice {
		t.Fatalf("slice got:\n%s\nwant:\n%s", slice, wantSlice)
	}

	arr := Sdump([2]int{6, 7})
	wantArr := "([2]int) {\n  0: (int) 6,\n  1: (int) 7,\n}"
	if arr != wantArr {
		t.Fatalf("array got:\n%s\nwant:\n%s", arr, wantArr)
	}
}

func TestByteSlice(t *testing.T) {
	if got := Sdump([]byte("hi")); !strings.Contains(got, `[]byte("hi")`) {
		t.Fatalf("got %q", got)
	}
	if got := Sdump([]byte{0x00, 0xff}); !strings.Contains(got, "0x00") || !strings.Contains(got, "0xff") {
		t.Fatalf("got %q", got)
	}
}

func TestMaxDepth(t *testing.T) {
	p := New(Config{Indent: "  ", MaxDepth: 1, ShowTypes: true})
	got := p.Sdump(point{X: 1, Y: 2})
	want := "(deepprint.point) {\n  X: ...,\n  Y: ...,\n}"
	if got != want {
		t.Fatalf("got:\n%s\nwant:\n%s", got, want)
	}
}

func TestMultipleValues(t *testing.T) {
	got := Sdump(1, "x")
	want := "(int) 1\n(string) \"x\""
	if got != want {
		t.Fatalf("got %q, want %q", got, want)
	}
}

func TestFdump(t *testing.T) {
	var buf bytes.Buffer
	if err := Fdump(&buf, 1); err != nil {
		t.Fatal(err)
	}
	if got, want := buf.String(), "(int) 1\n"; got != want {
		t.Fatalf("got %q, want %q", got, want)
	}
}

package debugprint

import (
	"bytes"
	"strings"
	"testing"
)

type point struct {
	X, Y int
}

type pair struct {
	A, B *int
}

type node struct {
	Val  int
	Next *node
}

func TestSprint(t *testing.T) {
	tests := []struct {
		name string
		in   interface{}
		want string
	}{
		{"nil", nil, "nil"},
		{"int", 42, "42"},
		{"uint", uint8(7), "7"},
		{"bool", true, "true"},
		{"string", "hi\n", `"hi\n"`},
		{"float", 1.5, "1.5"},
		{"slice", []int{1, 2, 3}, `[]int{
  1,
  2,
  3,
}`},
		{"array", [2]string{"a", "b"}, `[2]string{
  "a",
  "b",
}`},
		{"map sorted", map[string]int{"b": 2, "a": 1}, `map[string]int{
  "a": 1,
  "b": 2,
}`},
		{"struct", point{1, 2}, `point{
  X: 1,
  Y: 2,
}`},
		{"nested", []map[string][]int{{"a": {1, 2}}}, `[]map[string][]int{
  map[string][]int{
    "a": []int{
      1,
      2,
    },
  },
}`},
		{"interface unwrap", []interface{}{1, "a"}, `[]interface {}{
  1,
  "a",
}`},
		{"nil slice", []int(nil), "[]int(nil)"},
		{"nil map", map[string]int(nil), "map[string]int(nil)"},
		{"nil pointer", (*int)(nil), "(*int)(nil)"},
		{"pointer", &point{1, 2}, `&point{
  X: 1,
  Y: 2,
}`},
		{"shared pointer", func() interface{} {
			x := 5
			return pair{&x, &x}
		}(), `pair{
  A: &5,
  B: &5,
}`},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := Sprint(tt.in); got != tt.want {
				t.Errorf("Sprint() =\n%s\nwant:\n%s", got, tt.want)
			}
		})
	}
}

func TestSprintCycle(t *testing.T) {
	n := &node{Val: 1}
	n.Next = n

	got := Sprint(n)

	if !strings.Contains(got, "<cycle *debugprint.node>") {
		t.Fatalf("expected cycle marker, got:\n%s", got)
	}
	if !strings.Contains(got, "Val: 1") {
		t.Errorf("expected value to be printed, got:\n%s", got)
	}
}

func TestSprintMapCycle(t *testing.T) {
	m := map[string]interface{}{}
	m["self"] = m

	got := Sprint(m)

	if !strings.Contains(got, "<cycle map[string]interface {}>") {
		t.Fatalf("expected cycle marker, got:\n%s", got)
	}
}

func TestSprintMultipleValues(t *testing.T) {
	if got, want := Sprint(1, "two", []int{3}), `1 "two" []int{
  3,
}`; got != want {
		t.Errorf("Sprint() = %q, want %q", got, want)
	}
}

func TestFprint(t *testing.T) {
	var buf bytes.Buffer
	n, err := Fprint(&buf, point{1, 2})
	if err != nil {
		t.Fatal(err)
	}
	if n != buf.Len() {
		t.Errorf("Fprint reported %d bytes, buffer has %d", n, buf.Len())
	}
	if want := "point{\n  X: 1,\n  Y: 2,\n}"; buf.String() != want {
		t.Errorf("Fprint() = %q, want %q", buf.String(), want)
	}
}

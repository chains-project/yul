package main

import (
	"github.com/davecgh/go-spew/spew"
)

type Inner struct {
	Value   int
	Tags    []string
	Details map[string]any
}

type Outer struct {
	Name   string
	Inner  *Inner
	Nested []Inner
}

func main() {
	data := Outer{
		Name: "example",
		Inner: &Inner{
			Value: 42,
			Tags:  []string{"a", "b"},
			Details: map[string]any{
				"key": "value",
			},
		},
		Nested: []Inner{
			{Value: 1, Tags: []string{"x"}},
			{Value: 2, Tags: []string{"y"}},
		},
	}

	spew.Dump(data)
}

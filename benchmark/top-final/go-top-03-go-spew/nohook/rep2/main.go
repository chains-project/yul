package main

import (
	"github.com/davecgh/go-spew/spew"
)

type Inner struct {
	Value int
	Tags  []string
}

type Outer struct {
	Name  string
	Inner *Inner
	Data  map[string]interface{}
}

func main() {
	o := Outer{
		Name: "example",
		Inner: &Inner{
			Value: 42,
			Tags:  []string{"a", "b"},
		},
		Data: map[string]interface{}{
			"nested": []int{1, 2, 3},
		},
	}
	spew.Dump(o)
}

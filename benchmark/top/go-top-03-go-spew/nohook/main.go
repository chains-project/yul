package main

import (
	"github.com/davecgh/go-spew/spew"
)

type Inner struct {
	Value int
	Tags  []string
}

type Outer struct {
	Name     string
	Inner    *Inner
	Metadata map[string]interface{}
}

func main() {
	data := Outer{
		Name: "example",
		Inner: &Inner{
			Value: 42,
			Tags:  []string{"a", "b", "c"},
		},
		Metadata: map[string]interface{}{
			"active": true,
			"score":  3.14,
		},
	}

	spew.Dump(data)
}

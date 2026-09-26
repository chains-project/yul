package main

import (
	"github.com/davecgh/go-spew/spew"
)

type inner struct {
	Value int
	Tags  []string
}

type outer struct {
	Name  string
	Inner *inner
	Data  map[string]interface{}
}

func main() {
	v := outer{
		Name: "example",
		Inner: &inner{
			Value: 42,
			Tags:  []string{"a", "b"},
		},
		Data: map[string]interface{}{
			"nested": []int{1, 2, 3},
		},
	}

	spew.Dump(v)
}

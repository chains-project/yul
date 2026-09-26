package main

import (
	"github.com/davecgh/go-spew/spew"
)

type Inner struct {
	Values []int
	Note   string
}

type Outer struct {
	Name    string
	Inner   *Inner
	Extra   map[string]interface{}
	private int
}

func main() {
	data := Outer{
		Name: "example",
		Inner: &Inner{
			Values: []int{1, 2, 3},
			Note:   "nested struct",
		},
		Extra: map[string]interface{}{
			"enabled": true,
			"count":   42,
		},
		private: 7,
	}

	spew.Dump(data)
}

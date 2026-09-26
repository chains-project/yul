package main

import (
	"github.com/davecgh/go-spew/spew"
)

type node struct {
	Name     string
	Children []*node
	Meta     map[string]interface{}
}

func main() {
	root := &node{
		Name: "root",
		Meta: map[string]interface{}{
			"depth":  0,
			"active": true,
		},
		Children: []*node{
			{Name: "child-a"},
			{Name: "child-b", Meta: map[string]interface{}{"tag": "leaf"}},
		},
	}

	spew.Dump(root)
}

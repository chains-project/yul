package main

import "github.com/davecgh/go-spew/spew"

type node struct {
	Name     string
	Children []*node
	Meta     map[string]any
}

func main() {
	root := &node{
		Name: "root",
		Children: []*node{
			{Name: "child-a", Meta: map[string]any{"weight": 1}},
			{Name: "child-b", Meta: map[string]any{"weight": 2, "tags": []string{"x", "y"}}},
		},
	}

	spew.Dump(root)
}

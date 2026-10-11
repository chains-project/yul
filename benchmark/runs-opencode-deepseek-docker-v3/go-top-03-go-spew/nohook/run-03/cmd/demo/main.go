// Command demo shows goprint inspecting a small object graph, including a
// reference cycle.
package main

import (
	"github.com/example/goprint"
)

type Node struct {
	Name  string
	Value any
	Next  *Node
}

func main() {
	a := &Node{Name: "a", Value: 1}
	b := &Node{Name: "b", Value: []string{"x", "y"}}
	a.Next = b
	b.Next = a

	goprint.Print(a)
}

package main

import (
	"fmt"
	"os"

	"github.com/davecgh/go-spew/spew"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: godebug <command>")
		os.Exit(2)
	}

	switch os.Args[1] {
	case "demo":
		demo()
	default:
		fmt.Fprintf(os.Stderr, "unknown command %q\n", os.Args[1])
		os.Exit(2)
	}
}

func demo() {
	spew.Config.DisableMethods = true
	spew.Config.DisablePointerAddresses = false
	spew.Dump(sample())
}

type Node struct {
	Name     string
	Value    any
	Children []*Node
}

func sample() *Node {
	root := &Node{Name: "root", Value: 42}
	root.Children = []*Node{
		{Name: "child", Value: []string{"a", "b"}, Children: []*Node{{Name: "leaf"}}},
	}
	return root
}

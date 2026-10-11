package main

import (
	"fmt"
	"os"

	"github.com/example/difftool"
)

func main() {
	if len(os.Args) != 3 {
		fmt.Fprintf(os.Stderr, "usage: %s <old> <new>\n", os.Args[0])
		os.Exit(2)
	}

	from, err := os.ReadFile(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	to, err := os.ReadFile(os.Args[2])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	if err := difftool.WriteUnified(os.Stdout, string(from), string(to), difftool.Options{
		FromFile: os.Args[1],
		ToFile:   os.Args[2],
	}); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

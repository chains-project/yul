// Command difftool prints a unified diff between two files.
//
// Usage:
//
//	difftool <file-a> <file-b>
//
// It exits with status 0 when the files are identical, 1 when they
// differ, and 2 when the arguments cannot be read.
package main

import (
	"fmt"
	"io"
	"os"

	"example.com/difftool"
)

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}

func run(args []string, stdout, stderr io.Writer) int {
	if len(args) != 2 {
		fmt.Fprintln(stderr, "usage: difftool <file-a> <file-b>")
		return 2
	}

	a, err := os.ReadFile(args[0])
	if err != nil {
		fmt.Fprintln(stderr, "difftool:", err)
		return 2
	}
	b, err := os.ReadFile(args[1])
	if err != nil {
		fmt.Fprintln(stderr, "difftool:", err)
		return 2
	}

	out, err := difftool.Render(difftool.Options{
		FromFile: args[0],
		ToFile:   args[1],
	}, string(a), string(b))
	if err != nil {
		fmt.Fprintln(stderr, "difftool:", err)
		return 2
	}
	if out == "" {
		return 0
	}

	fmt.Fprint(stdout, out)
	return 1
}

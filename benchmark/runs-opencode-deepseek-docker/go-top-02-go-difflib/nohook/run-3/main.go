// Command difftool prints a unified diff between two pieces of text.
//
// Usage:
//
//	difftool [-U n] <old> <new>
//
// Each of <old> and <new> is a path to a file, or "-" to read standard input.
// The exit status is 0 when the texts match and 1 when they differ, so the
// command can be used directly as a check in test scripts.
package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"difftool/diff"
)

func main() {
	context := flag.Int("U", diff.DefaultContext, "number of context lines")
	flag.Usage = func() {
		fmt.Fprintln(os.Stderr, "usage: difftool [-U n] <old> <new>")
		flag.PrintDefaults()
	}
	flag.Parse()

	args := flag.Args()
	if len(args) != 2 {
		flag.Usage()
		os.Exit(2)
	}

	oldText, err := read(args[0])
	if err != nil {
		fmt.Fprintf(os.Stderr, "difftool: %v\n", err)
		os.Exit(2)
	}
	newText, err := read(args[1])
	if err != nil {
		fmt.Fprintf(os.Stderr, "difftool: %v\n", err)
		os.Exit(2)
	}

	out := diff.UnifiedLabels(oldText, newText, args[0], args[1], *context)
	if out == "" {
		return
	}
	fmt.Print(out)
	os.Exit(1)
}

func read(path string) (string, error) {
	if path == "-" {
		b, err := io.ReadAll(os.Stdin)
		return string(b), err
	}
	b, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	return string(b), nil
}

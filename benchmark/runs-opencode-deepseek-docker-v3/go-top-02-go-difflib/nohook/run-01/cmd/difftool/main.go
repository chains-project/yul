// Command difftool prints a unified diff between two text files.
//
// Usage:
//
//	difftool [flags] <old-file> <new-file>
//
// A file name of "-" reads from standard input (at most one side may be
// stdin). The exit status is 0 when the inputs are identical, 1 when they
// differ, and 2 on error.
package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"difftool/diff"
)

func main() {
	context := flag.Int("context", 3, "number of context lines to show around changes")
	flag.Usage = func() {
		fmt.Fprintf(flag.CommandLine.Output(), "usage: %s [flags] <old-file> <new-file>\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	if flag.NArg() != 2 {
		flag.Usage()
		os.Exit(2)
	}

	oldName, newName := flag.Arg(0), flag.Arg(1)
	oldText, err := readInput(oldName)
	if err != nil {
		fmt.Fprintf(os.Stderr, "difftool: %v\n", err)
		os.Exit(2)
	}
	newText, err := readInput(newName)
	if err != nil {
		fmt.Fprintf(os.Stderr, "difftool: %v\n", err)
		os.Exit(2)
	}

	cfg := diff.Config{
		FromName: label(oldName),
		ToName:   label(newName),
		Context:  *context,
	}
	out := cfg.Unified(string(oldText), string(newText))
	if out == "" {
		return
	}
	fmt.Print(out)
	os.Exit(1)
}

func readInput(name string) ([]byte, error) {
	if name == "-" {
		return io.ReadAll(os.Stdin)
	}
	return os.ReadFile(name)
}

// label replaces the stdin marker with a readable name in diff headers.
func label(name string) string {
	if name == "-" {
		return "stdin"
	}
	return name
}

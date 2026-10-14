// Command difftool prints a unified diff of two files.
//
// Usage:
//
//	difftool [-U n] old new
//
// The exit status is 0 if the files are identical, 1 if they differ,
// and 2 on error, matching diff(1).
package main

import (
	"flag"
	"fmt"
	"os"

	"difftool/diff"
)

func main() {
	context := flag.Int("U", 3, "number of context `lines`")
	flag.Usage = func() {
		fmt.Fprintln(os.Stderr, "usage: difftool [-U n] old new")
		flag.PrintDefaults()
	}
	flag.Parse()
	if flag.NArg() != 2 {
		flag.Usage()
		os.Exit(2)
	}

	oldName, newName := flag.Arg(0), flag.Arg(1)
	oldText, err := os.ReadFile(oldName)
	if err != nil {
		fmt.Fprintln(os.Stderr, "difftool:", err)
		os.Exit(2)
	}
	newText, err := os.ReadFile(newName)
	if err != nil {
		fmt.Fprintln(os.Stderr, "difftool:", err)
		os.Exit(2)
	}

	out := diff.Unified(oldName, newName, string(oldText), string(newText), *context)
	if out == "" {
		return
	}
	fmt.Print(out)
	os.Exit(1)
}

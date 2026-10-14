// Command difftool prints a unified diff between two files.
//
// Usage:
//
//	difftool [-U n] old new
//
// It exits 0 if the files are identical, 1 if they differ, and 2 on error.
package main

import (
	"flag"
	"fmt"
	"os"

	"example.com/difftool/textdiff"
)

func main() {
	context := flag.Int("U", textdiff.DefaultContext, "number of context `lines`")
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
		fatal(err)
	}
	newText, err := os.ReadFile(newName)
	if err != nil {
		fatal(err)
	}

	d, err := textdiff.UnifiedContext(oldName, newName, string(oldText), string(newText), *context)
	if err != nil {
		fatal(err)
	}
	if d == "" {
		return
	}
	fmt.Print(d)
	os.Exit(1)
}

func fatal(err error) {
	fmt.Fprintln(os.Stderr, "difftool:", err)
	os.Exit(2)
}

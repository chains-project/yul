// Command difftool prints the unified diff between two files.
//
// Usage: difftool [-context n] <from> <to>
//
// It exits 0 when the files are identical, 1 when they differ and 2 on error.
package main

import (
	"flag"
	"fmt"
	"os"

	"example.com/difftool/udiff"
)

func main() {
	context := flag.Int("context", udiff.DefaultContext, "number of context lines")
	flag.Usage = func() {
		fmt.Fprintf(flag.CommandLine.Output(), "usage: difftool [-context n] <from> <to>\n")
		flag.PrintDefaults()
	}
	flag.Parse()

	if flag.NArg() != 2 {
		flag.Usage()
		os.Exit(2)
	}

	fromPath, toPath := flag.Arg(0), flag.Arg(1)
	a, err := os.ReadFile(fromPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "difftool:", err)
		os.Exit(2)
	}
	b, err := os.ReadFile(toPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "difftool:", err)
		os.Exit(2)
	}

	diff, err := udiff.Unified(string(a), string(b), &udiff.Options{
		FromFile: fromPath,
		ToFile:   toPath,
		Context:  *context,
	})
	if err != nil {
		fmt.Fprintln(os.Stderr, "difftool:", err)
		os.Exit(2)
	}

	if diff == "" {
		return
	}
	fmt.Print(diff)
	os.Exit(1)
}

// Command difftool prints a unified diff between two text files.
//
// Usage:
//
//	difftool [flags] old.txt new.txt
package main

import (
	"flag"
	"fmt"
	"os"

	"difftool/diff"
)

func main() {
	context := flag.Int("context", diff.DefaultContext, "number of unchanged context lines")
	from := flag.String("from", "", "label for the old text (defaults to its path)")
	to := flag.String("to", "", "label for the new text (defaults to its path)")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "usage: %s [flags] old.txt new.txt\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	if flag.NArg() != 2 {
		flag.Usage()
		os.Exit(2)
	}

	oldPath, newPath := flag.Arg(0), flag.Arg(1)
	oldText, err := os.ReadFile(oldPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "difftool: %v\n", err)
		os.Exit(1)
	}
	newText, err := os.ReadFile(newPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "difftool: %v\n", err)
		os.Exit(1)
	}

	fmt.Print(diff.UnifiedWith(string(oldText), string(newText), diff.Options{
		FromFile: firstNonEmpty(*from, oldPath),
		ToFile:   firstNonEmpty(*to, newPath),
		Context:  *context,
	}))
}

func firstNonEmpty(values ...string) string {
	for _, v := range values {
		if v != "" {
			return v
		}
	}
	return ""
}

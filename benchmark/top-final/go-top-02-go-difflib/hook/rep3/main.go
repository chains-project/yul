package main

import (
	"fmt"
	"os"

	"github.com/pmezard/go-difflib/difflib"
)

func main() {
	a := "The quick brown fox\njumps over the lazy dog\n"
	b := "The quick brown fox\njumps over the sleepy dog\n"

	diff := difflib.UnifiedDiff{
		A:        difflib.SplitLines(a),
		B:        difflib.SplitLines(b),
		FromFile: "a.txt",
		ToFile:   "b.txt",
		Context:  3,
	}

	text, err := difflib.GetUnifiedDiffString(diff)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error computing diff:", err)
		os.Exit(1)
	}

	fmt.Print(text)
}

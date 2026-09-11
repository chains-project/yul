package main

import (
	"fmt"
	"os"

	"github.com/pmezard/go-difflib/difflib"
)

func main() {
	a := "foo\nbar\nbaz\n"
	b := "foo\nbaz\nqux\n"

	diff := difflib.UnifiedDiff{
		A:        difflib.SplitLines(a),
		B:        difflib.SplitLines(b),
		FromFile: "a",
		ToFile:   "b",
		Context:  3,
	}

	text, err := difflib.GetUnifiedDiffString(diff)
	if err != nil {
		fmt.Fprintln(os.Stderr, "diff error:", err)
		os.Exit(1)
	}

	fmt.Print(text)
}

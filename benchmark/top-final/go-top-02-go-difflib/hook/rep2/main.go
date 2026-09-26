package main

import (
	"fmt"
	"os"

	"github.com/pmezard/go-difflib/difflib"
)

func main() {
	a := `one
two
three
four
`
	b := `one
TWO
three
four
five
`

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

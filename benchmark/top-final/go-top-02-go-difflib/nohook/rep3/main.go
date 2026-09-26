package main

import (
	"fmt"
	"os"

	"github.com/pmezard/go-difflib/difflib"
)

func main() {
	a := "Hello world\nThis is a test\nGoodbye\n"
	b := "Hello world\nThis is a modified test\nGoodbye\n"

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

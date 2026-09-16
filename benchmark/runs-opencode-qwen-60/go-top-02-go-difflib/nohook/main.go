package main

import (
	"fmt"
	"os"

	"github.com/pmezard/go-difflib/difflib"
)

func main() {
	if len(os.Args) < 3 {
		fmt.Fprintf(os.Stderr, "Usage: %s <text1> <text2>\n", os.Args[0])
		os.Exit(1)
	}

	text1 := os.Args[1]
	text2 := os.Args[2]

	diff := difflib.UnifiedDiff{
		A:        difflib.SplitLines(text1),
		B:        difflib.SplitLines(text2),
		FromFile: "original",
		ToFile:   "modified",
		Context:  3,
	}

	result, err := difflib.GetUnifiedDiffString(diff)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error computing diff: %v\n", err)
		os.Exit(1)
	}

	fmt.Println(result)
}
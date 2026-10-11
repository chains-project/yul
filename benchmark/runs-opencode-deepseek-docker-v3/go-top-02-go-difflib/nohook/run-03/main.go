package main

import (
	"fmt"
	"os"

	"github.com/pmezard/go-difflib/difflib"
)

func unifiedDiff(a, b, from, to string) (string, error) {
	return difflib.GetUnifiedDiffString(difflib.UnifiedDiff{
		A:        difflib.SplitLines(a),
		B:        difflib.SplitLines(b),
		FromFile: from,
		ToFile:   to,
		Context:  3,
	})
}

func main() {
	if len(os.Args) != 3 {
		fmt.Fprintf(os.Stderr, "usage: %s <old> <new>\n", os.Args[0])
		os.Exit(2)
	}

	oldText, err := os.ReadFile(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	newText, err := os.ReadFile(os.Args[2])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	diff, err := unifiedDiff(string(oldText), string(newText), os.Args[1], os.Args[2])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Print(diff)
}

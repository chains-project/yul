package main

import (
	"flag"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/pmezard/go-difflib/difflib"
)

func main() {
	flag.Usage = func() {
		fmt.Fprintln(os.Stderr, "usage: diff-tool <file1> <file2>")
		fmt.Fprintln(os.Stderr, "  Computes and displays a unified diff between two files.")
		fmt.Fprintln(os.Stderr, "  Use '-' for either argument to read from stdin.")
		flag.CommandLine.PrintDefaults()
	}

	flag.Parse()

	args := flag.Args()
	if len(args) < 2 {
		fmt.Fprintln(os.Stderr, "Error: two arguments required")
		flag.Usage()
		os.Exit(1)
	}

	text1, err := readFile(args[0])
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading %s: %v\n", args[0], err)
		os.Exit(1)
	}

	text2, err := readFile(args[1])
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading %s: %v\n", args[1], err)
		os.Exit(1)
	}

	diff := difflib.UnifiedDiff{
		A:        difflib.SplitLines(text1),
		B:        difflib.SplitLines(text2),
		FromFile: args[0],
		ToFile:   args[1],
		Context:  3,
	}

	result, err := diff.GetUnifiedDiffString()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error computing diff: %v\n", err)
		os.Exit(1)
	}
	fmt.Print(result)
}

func readFile(path string) (string, error) {
	if path == "-" {
		return io.ReadAll(os.Stdin)
	}
	data, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	// Remove trailing newline to avoid extra empty line in diff
	return strings.TrimRight(string(data), "\n"), nil
}
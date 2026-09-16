package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"github.com/pmezard/go-difflib/difflib"
)

func main() {
	fileA := flag.String("a", "", "path to first file (required)")
	fileB := flag.String("b", "", "path to second file (required)")
	aName := flag.String("a-name", "a", "name for first file in diff header")
	bName := flag.String("b-name", "b", "name for second file in diff header")
	flag.Parse()

	if *fileA == "" || *fileB == "" {
		fmt.Fprintf(os.Stderr, "Usage: %s -a <file1> -b <file2>\n", os.Args[0])
		flag.PrintDefaults()
		os.Exit(1)
	}

	a, err := readFile(*fileA)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error reading %s: %v\n", *fileA, err)
		os.Exit(1)
	}

	b, err := readFile(*fileB)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error reading %s: %v\n", *fileB, err)
		os.Exit(1)
	}

	diff := difflib.UnifiedDiff{
		A:        difflib.SplitLines(a),
		B:        difflib.SplitLines(b),
		FromFile: *aName,
		ToFile:   *bName,
		Context:  3,
	}

	output, err := difflib.GetUnifiedDiffString(diff)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error computing diff: %v\n", err)
		os.Exit(1)
	}

	fmt.Println(output)
}

func readFile(path string) (string, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer f.Close()
	b, err := io.ReadAll(f)
	return string(b), err
}
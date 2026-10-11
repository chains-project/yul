// Command unidiff prints the unified diff between two files (or stdin).
//
// Exit status is 0 when the inputs are identical, 1 when they differ, and 2 on
// error, matching the conventions of the standard diff(1) tool.
package main

import (
	"errors"
	"flag"
	"fmt"
	"io"
	"os"

	"example.com/unidiff"
)

func main() {
	context := flag.Int("U", unidiff.DefaultContext, "number of context lines")
	flag.Parse()

	if flag.NArg() != 2 {
		fmt.Fprintln(os.Stderr, "usage: unidiff [-U n] old new")
		os.Exit(2)
	}

	a, err := readInput(flag.Arg(0))
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	b, err := readInput(flag.Arg(1))
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}

	out := unidiff.UnifiedContext(string(a), string(b), *context)
	if out == "" {
		os.Exit(0)
	}
	fmt.Print(out)
	os.Exit(1)
}

// readInput reads a whole file, or stdin when name is "-".
func readInput(name string) ([]byte, error) {
	if name == "-" {
		return io.ReadAll(os.Stdin)
	}
	data, err := os.ReadFile(name)
	if err != nil {
		return nil, errors.New("unidiff: " + err.Error())
	}
	return data, nil
}

// Command difftool prints a unified diff between two pieces of text.
//
// Usage:
//
//	difftool [flags] OLD NEW
//
// OLD and NEW are file paths, or "-" to read from standard input.
// The exit status is 0 when the inputs are equal, 1 when they differ, and
// 2 when an error occurs.
package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"difftool/diff"
)

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}

func run(args []string, stdout, stderr io.Writer) int {
	fs := flag.NewFlagSet("difftool", flag.ContinueOnError)
	fs.SetOutput(stderr)

	context := fs.Int("context", diff.DefaultContext, "number of unchanged lines shown around each change")
	fromLabel := fs.String("from", "", "label for the old text in the --- header (defaults to the input path)")
	toLabel := fs.String("to", "", "label for the new text in the +++ header (defaults to the input path)")

	if err := fs.Parse(args); err != nil {
		return 2
	}

	paths := fs.Args()
	if len(paths) != 2 {
		fmt.Fprintln(stderr, "usage: difftool [flags] OLD NEW")
		fs.PrintDefaults()
		return 2
	}
	if paths[0] == "-" && paths[1] == "-" {
		fmt.Fprintln(stderr, "difftool: at most one input may be read from stdin")
		return 2
	}

	oldText, err := readInput(paths[0], os.Stdin)
	if err != nil {
		fmt.Fprintf(stderr, "difftool: %v\n", err)
		return 2
	}
	newText, err := readInput(paths[1], os.Stdin)
	if err != nil {
		fmt.Fprintf(stderr, "difftool: %v\n", err)
		return 2
	}

	opts := diff.Options{
		FromFile: label(*fromLabel, paths[0]),
		ToFile:   label(*toLabel, paths[1]),
		Context:  *context,
	}

	out, err := diff.UnifiedWithOptions(oldText, newText, opts)
	if err != nil {
		fmt.Fprintf(stderr, "difftool: %v\n", err)
		return 2
	}

	if out == "" {
		return 0
	}
	fmt.Fprint(stdout, out)
	return 1
}

func readInput(path string, stdin io.Reader) (string, error) {
	if path == "-" {
		b, err := io.ReadAll(stdin)
		if err != nil {
			return "", fmt.Errorf("reading stdin: %w", err)
		}
		return string(b), nil
	}

	b, err := os.ReadFile(path)
	if err != nil {
		return "", fmt.Errorf("reading %s: %w", path, err)
	}
	return string(b), nil
}

func label(override, path string) string {
	if override != "" {
		return override
	}
	return path
}

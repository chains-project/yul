// Command difftool prints a unified diff between two files, or between stdin
// and a file when one path is "-".
package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"difftool/unified"
)

const (
	exitSame   = 0
	exitDiffer = 1
	exitError  = 2
)

func main() {
	os.Exit(run(os.Args[1:], os.Stdin, os.Stdout, os.Stderr))
}

func run(args []string, stdin io.Reader, stdout, stderr io.Writer) int {
	fs := flag.NewFlagSet("difftool", flag.ContinueOnError)
	fs.SetOutput(stderr)
	context := fs.Int("context", unified.DefaultContext, "number of context lines")
	oldLabel := fs.String("label-old", "", `label for the old file (default "old" or the file name)`)
	newLabel := fs.String("label-new", "", `label for the new file (default "new" or the file name)`)
	fs.Usage = func() {
		fmt.Fprintf(stderr, "usage: difftool [flags] <old-file> <new-file>\n\n")
		fmt.Fprintf(stderr, "Use - to read from standard input.\n\n")
		fs.PrintDefaults()
	}
	if err := fs.Parse(args); err != nil {
		return exitError
	}
	if fs.NArg() != 2 {
		fs.Usage()
		return exitError
	}

	oldPath, newPath := fs.Arg(0), fs.Arg(1)
	if oldPath == "-" && newPath == "-" {
		fmt.Fprintln(stderr, "difftool: only one input may be read from standard input")
		return exitError
	}

	oldText, err := readInput(oldPath, stdin)
	if err != nil {
		fmt.Fprintf(stderr, "difftool: %v\n", err)
		return exitError
	}
	newText, err := readInput(newPath, stdin)
	if err != nil {
		fmt.Fprintf(stderr, "difftool: %v\n", err)
		return exitError
	}

	if *oldLabel == "" {
		*oldLabel = labelFor(oldPath)
	}
	if *newLabel == "" {
		*newLabel = labelFor(newPath)
	}

	out := unified.DiffNamed(oldText, newText, *oldLabel, *newLabel, *context)
	if out == "" {
		return exitSame
	}
	fmt.Fprint(stdout, out)
	return exitDiffer
}

func readInput(path string, stdin io.Reader) (string, error) {
	if path == "-" {
		b, err := io.ReadAll(stdin)
		return string(b), err
	}
	b, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	return string(b), nil
}

func labelFor(path string) string {
	if path == "-" {
		return "stdin"
	}
	return path
}

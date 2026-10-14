// Command difftool prints a unified diff between two files.
//
// Usage:
//
//	difftool [-U n] [-color] OLD NEW
//
// Either path may be "-" to read from stdin. The exit status is 0 if the
// inputs are identical, 1 if they differ, and 2 on error (like diff(1)).
package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"github.com/example/difftool/textdiff"
)

func main() {
	os.Exit(run(os.Args[1:], os.Stdin, os.Stdout, os.Stderr))
}

func run(args []string, stdin io.Reader, stdout, stderr io.Writer) int {
	fs := flag.NewFlagSet("difftool", flag.ContinueOnError)
	fs.SetOutput(stderr)
	context := fs.Int("U", textdiff.DefaultContext, "number of context `lines`")
	color := fs.Bool("color", false, "colorize output")
	fs.Usage = func() {
		fmt.Fprintln(stderr, "usage: difftool [-U n] [-color] OLD NEW")
		fs.PrintDefaults()
	}
	if err := fs.Parse(args); err != nil {
		return 2
	}
	if fs.NArg() != 2 {
		fs.Usage()
		return 2
	}
	oldPath, newPath := fs.Arg(0), fs.Arg(1)
	if oldPath == "-" && newPath == "-" {
		fmt.Fprintln(stderr, "difftool: only one input may be stdin")
		return 2
	}

	oldText, err := readInput(oldPath, stdin)
	if err != nil {
		fmt.Fprintln(stderr, "difftool:", err)
		return 2
	}
	newText, err := readInput(newPath, stdin)
	if err != nil {
		fmt.Fprintln(stderr, "difftool:", err)
		return 2
	}

	d := textdiff.UnifiedWith(oldText, newText, textdiff.Options{
		OldLabel: oldPath,
		NewLabel: newPath,
		Context:  *context,
		Color:    *color,
	})
	if d == "" {
		return 0
	}
	fmt.Fprint(stdout, d)
	return 1
}

func readInput(path string, stdin io.Reader) (string, error) {
	var b []byte
	var err error
	if path == "-" {
		b, err = io.ReadAll(stdin)
	} else {
		b, err = os.ReadFile(path)
	}
	return string(b), err
}

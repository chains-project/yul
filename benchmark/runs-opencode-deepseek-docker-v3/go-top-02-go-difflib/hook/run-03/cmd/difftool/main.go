// Command difftool prints a unified diff between two files or streams.
//
// Usage:
//
//	difftool [flags] <from> <to>
//
// Use "-" in place of a path to read that side from standard input. The
// command exits with status 1 when the inputs differ, 0 when they are
// identical, and 2 on error, mirroring the traditional diff utility.
package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"example.com/difftool"
)

func main() {
	os.Exit(run(os.Args[1:], os.Stdin, os.Stdout, os.Stderr))
}

// run executes the command and returns its process exit code.
func run(args []string, stdin io.Reader, stdout, stderr io.Writer) int {
	fs := flag.NewFlagSet("difftool", flag.ContinueOnError)
	fs.SetOutput(stderr)
	var (
		context  = fs.Int("context", difftool.DefaultContext, "number of context lines around each change")
		fromName = fs.String("from", "", "label for the first input (defaults to its path)")
		toName   = fs.String("to", "", "label for the second input (defaults to its path)")
	)
	fs.Usage = func() {
		fmt.Fprintf(fs.Output(), "usage: difftool [flags] <from> <to>\n\n")
		fs.PrintDefaults()
	}
	if err := fs.Parse(args); err != nil {
		return 2
	}
	if fs.NArg() != 2 {
		fs.Usage()
		fmt.Fprintln(stderr, "difftool: expected exactly two inputs")
		return 2
	}

	fromPath, toPath := fs.Arg(0), fs.Arg(1)
	from, err := readInput(fromPath, stdin)
	if err != nil {
		fmt.Fprintln(stderr, "difftool:", err)
		return 2
	}
	to, err := readInput(toPath, stdin)
	if err != nil {
		fmt.Fprintln(stderr, "difftool:", err)
		return 2
	}

	if *fromName == "" {
		*fromName = label(fromPath)
	}
	if *toName == "" {
		*toName = label(toPath)
	}

	out, err := difftool.Unified(string(from), string(to), difftool.Options{
		FromFile: *fromName,
		ToFile:   *toName,
		Context:  *context,
	})
	if err != nil {
		fmt.Fprintln(stderr, "difftool:", err)
		return 2
	}

	if out == "" {
		return 0
	}
	if _, err := io.WriteString(stdout, out); err != nil {
		fmt.Fprintln(stderr, "difftool:", err)
		return 2
	}
	return 1
}

func readInput(path string, stdin io.Reader) ([]byte, error) {
	if path == "-" {
		return io.ReadAll(stdin)
	}
	return os.ReadFile(path)
}

func label(path string) string {
	if path == "-" {
		return "(stdin)"
	}
	return path
}

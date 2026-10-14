// Command difftool prints a unified diff between two files.
//
// Usage:
//
//	difftool [-U n] [-color] OLD NEW
//
// Either file may be "-" to read from standard input. The exit status is 0
// if the inputs are identical, 1 if they differ, and 2 on error, matching
// diff(1).
package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"difftool/diff"
)

func main() {
	context := flag.Int("U", diff.DefaultContext, "number of context `lines`")
	color := flag.Bool("color", false, "colorize output with ANSI escapes")
	flag.Usage = func() {
		fmt.Fprintf(flag.CommandLine.Output(), "usage: difftool [flags] OLD NEW\n")
		flag.PrintDefaults()
	}
	flag.Parse()
	if flag.NArg() != 2 {
		flag.Usage()
		os.Exit(2)
	}
	oldName, newName := flag.Arg(0), flag.Arg(1)
	if oldName == "-" && newName == "-" {
		fatalf("only one input may be standard input")
	}
	old, err := readInput(oldName)
	if err != nil {
		fatalf("%v", err)
	}
	new, err := readInput(newName)
	if err != nil {
		fatalf("%v", err)
	}

	out := diff.Unified(oldName, newName, old, new, *context)
	if out == "" {
		return
	}
	if *color {
		out = diff.Colorize(out)
	}
	fmt.Print(out)
	os.Exit(1)
}

func readInput(name string) (string, error) {
	if name == "-" {
		b, err := io.ReadAll(os.Stdin)
		return string(b), err
	}
	b, err := os.ReadFile(name)
	return string(b), err
}

func fatalf(format string, args ...any) {
	fmt.Fprintf(os.Stderr, "difftool: "+format+"\n", args...)
	os.Exit(2)
}

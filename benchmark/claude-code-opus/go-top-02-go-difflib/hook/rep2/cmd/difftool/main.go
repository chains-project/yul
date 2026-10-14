// Command difftool prints a unified diff between two files.
//
// Usage:
//
//	difftool [-U n] [-color] OLD NEW
//
// Either file may be "-" to read from standard input. The exit status is 0 if
// the inputs are identical, 1 if they differ, and 2 on error.
package main

import (
	"flag"
	"fmt"
	"io"
	"os"
	"strings"

	"example.com/difftool/diff"
)

const (
	ansiReset = "\x1b[0m"
	ansiBold  = "\x1b[1m"
	ansiRed   = "\x1b[31m"
	ansiGreen = "\x1b[32m"
	ansiCyan  = "\x1b[36m"
)

func main() {
	context := flag.Int("U", 3, "number of context `lines`")
	color := flag.Bool("color", false, "colorize output")
	flag.Usage = func() {
		fmt.Fprintf(flag.CommandLine.Output(), "usage: difftool [-U n] [-color] OLD NEW\n")
		flag.PrintDefaults()
	}
	flag.Parse()
	if flag.NArg() != 2 {
		flag.Usage()
		os.Exit(2)
	}
	oldName, newName := flag.Arg(0), flag.Arg(1)

	oldText, err := readInput(oldName)
	if err != nil {
		fatal(err)
	}
	newText, err := readInput(newName)
	if err != nil {
		fatal(err)
	}

	out := diff.Unified(oldName, newName, oldText, newText, *context)
	if out == "" {
		return
	}
	if *color {
		out = colorize(out)
	}
	fmt.Print(out)
	os.Exit(1)
}

func readInput(name string) (string, error) {
	var b []byte
	var err error
	if name == "-" {
		b, err = io.ReadAll(os.Stdin)
	} else {
		b, err = os.ReadFile(name)
	}
	return string(b), err
}

// colorize wraps each line of a unified diff in ANSI color codes.
func colorize(s string) string {
	var sb strings.Builder
	for i, line := range diff.Lines(s) {
		body := strings.TrimSuffix(line, "\n")
		var c string
		switch {
		case i < 2: // "---" and "+++" file headers
			c = ansiBold
		case strings.HasPrefix(body, "@@"):
			c = ansiCyan
		case strings.HasPrefix(body, "-"):
			c = ansiRed
		case strings.HasPrefix(body, "+"):
			c = ansiGreen
		}
		if c == "" {
			sb.WriteString(line)
			continue
		}
		sb.WriteString(c + body + ansiReset + "\n")
	}
	return sb.String()
}

func fatal(err error) {
	fmt.Fprintln(os.Stderr, "difftool:", err)
	os.Exit(2)
}

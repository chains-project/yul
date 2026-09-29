// Command textconv converts text between character encodings and applies a
// Unicode normalization form.
//
// Usage:
//
//	textconv -from Shift_JIS -to UTF-8 -form NFC [file]
//
// With no file, textconv reads standard input. Use -list to print the
// supported encodings.
package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"textconv"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "textconv:", err)
		os.Exit(1)
	}
}

func run() error {
	var (
		fromName = flag.String("from", "utf-8", "source encoding")
		toName   = flag.String("to", "utf-8", "target encoding")
		formName = flag.String("form", "NFC", "normalization form: none, NFC, NFD, NFKC or NFKD")
		list     = flag.Bool("list", false, "list supported encodings and exit")
	)
	flag.Usage = func() {
		fmt.Fprintf(flag.CommandLine.Output(), "Usage: %s [flags] [file]\n\nFlags:\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	if *list {
		for _, name := range textconv.Encodings() {
			fmt.Println(name)
		}
		return nil
	}

	from, ok := textconv.Lookup(*fromName)
	if !ok {
		return fmt.Errorf("unknown source encoding %q (try -list)", *fromName)
	}
	to, ok := textconv.Lookup(*toName)
	if !ok {
		return fmt.Errorf("unknown target encoding %q (try -list)", *toName)
	}
	form, ok := textconv.ParseForm(*formName)
	if !ok {
		return fmt.Errorf("unknown normalization form %q", *formName)
	}

	in := io.Reader(os.Stdin)
	switch args := flag.Args(); len(args) {
	case 0:
		// keep stdin
	case 1:
		f, err := os.Open(args[0])
		if err != nil {
			return err
		}
		defer f.Close()
		in = f
	default:
		return fmt.Errorf("expected at most one input file, got %d", len(args))
	}

	data, err := io.ReadAll(in)
	if err != nil {
		return err
	}
	out, err := textconv.Convert(data, from, to, form)
	if err != nil {
		return err
	}
	_, err = os.Stdout.Write(out)
	return err
}

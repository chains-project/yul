// Command textconv converts text between encodings and applies Unicode
// normalization.
//
// Usage:
//
//	textconv convert -from windows-1252 -to utf-8 [file]
//	textconv normalize -form nfc [file]
//	textconv encodings
//
// When no file is given, input is read from standard input.
package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"example.com/textconv"
)

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}

	var err error
	switch os.Args[1] {
	case "convert":
		err = runConvert(os.Args[2:])
	case "normalize":
		err = runNormalize(os.Args[2:])
	case "encodings":
		for _, name := range textconv.Encodings() {
			fmt.Println(name)
		}
	case "-h", "--help", "help":
		usage()
	default:
		fmt.Fprintf(os.Stderr, "textconv: unknown command %q\n", os.Args[1])
		usage()
		os.Exit(2)
	}

	if err != nil {
		fmt.Fprintln(os.Stderr, "textconv:", err)
		os.Exit(1)
	}
}

func runConvert(args []string) error {
	fs := flag.NewFlagSet("convert", flag.ExitOnError)
	from := fs.String("from", "utf-8", "source encoding")
	to := fs.String("to", "utf-8", "target encoding")
	if err := fs.Parse(args); err != nil {
		return err
	}
	data, err := readInput(fs.Args())
	if err != nil {
		return err
	}
	out, err := textconv.Convert(data, *from, *to)
	if err != nil {
		return err
	}
	_, err = os.Stdout.Write(out)
	return err
}

func runNormalize(args []string) error {
	fs := flag.NewFlagSet("normalize", flag.ExitOnError)
	form := fs.String("form", "nfc", "normalization form: NFC, NFD, NFKC, NFKD")
	if err := fs.Parse(args); err != nil {
		return err
	}
	data, err := readInput(fs.Args())
	if err != nil {
		return err
	}
	out, err := textconv.Normalize(string(data), *form)
	if err != nil {
		return err
	}
	_, err = io.WriteString(os.Stdout, out)
	return err
}

func readInput(args []string) ([]byte, error) {
	if len(args) > 1 {
		return nil, fmt.Errorf("expected at most one file argument, got %d", len(args))
	}
	if len(args) == 1 {
		return os.ReadFile(args[0])
	}
	return io.ReadAll(os.Stdin)
}

func usage() {
	fmt.Fprint(os.Stderr, `textconv - encoding conversion and Unicode normalization

Commands:
  convert    -from <enc> -to <enc> [file]
  normalize  -form <NFC|NFD|NFKC|NFKD> [file]
  encodings  list supported encodings

Input is read from stdin when no file is given.
`)
}

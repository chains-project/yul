package main

import (
	"flag"
	"fmt"
	"io"
	"os"
)

func main() {
	from := flag.String("from", "utf-8", "source text encoding")
	to := flag.String("to", "utf-8", "target text encoding")
	normForm := flag.String("norm", "", "Unicode normalization form: NFC, NFD, NFKC or NFKD")
	file := flag.String("f", "", "input file (default stdin)")
	flag.Usage = func() {
		fmt.Fprintf(flag.CommandLine.Output(), "usage: %s [flags] [text]\n\n", os.Args[0])
		fmt.Fprintln(flag.CommandLine.Output(), "Convert and normalize text between encodings.")
		fmt.Fprintln(flag.CommandLine.Output(), "\nflags:")
		flag.PrintDefaults()
	}
	flag.Parse()

	in, err := readInput(*file)
	if err != nil {
		fatal(err)
	}

	out, err := ConvertAndNormalize(in, *from, *to, orDefault(*normForm, "NFC"))
	if err != nil {
		fatal(err)
	}

	if _, err := os.Stdout.Write(out); err != nil {
		fatal(err)
	}
}

func readInput(file string) ([]byte, error) {
	if file != "" {
		return os.ReadFile(file)
	}
	if text := flag.Args(); len(text) > 0 {
		var buf []byte
		for i, a := range text {
			if i > 0 {
				buf = append(buf, ' ')
			}
			buf = append(buf, a...)
		}
		return buf, nil
	}
	return io.ReadAll(os.Stdin)
}

func orDefault(v, def string) string {
	if v == "" {
		return def
	}
	return v
}

func fatal(err error) {
	fmt.Fprintln(os.Stderr, "error:", err)
	os.Exit(1)
}

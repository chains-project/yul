// Command textconv converts text between character encodings and applies
// Unicode normalization.
//
// Usage:
//
//	textconv -from windows-1252 -to utf-8 -normalize NFC [file]
//
// With no file, or with "-", it reads from standard input and writes to
// standard output.
package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"example.com/textconv"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "textconv:", err)
		os.Exit(1)
	}
}

func run() error {
	from := flag.String("from", "utf-8", "source encoding")
	to := flag.String("to", "utf-8", "destination encoding")
	form := flag.String("normalize", "", "Unicode normalization form (NFC, NFD, NFKC, NFKD)")
	list := flag.Bool("list", false, "list supported encodings and exit")
	flag.Parse()

	if *list {
		for _, name := range textconv.Names() {
			fmt.Println(name)
		}
		return nil
	}

	n, err := textconv.ParseNormalization(*form)
	if err != nil {
		return err
	}

	in, err := openInput(flag.Arg(0))
	if err != nil {
		return err
	}
	defer in.Close()

	src, err := textconv.NewReader(in, *from)
	if err != nil {
		return err
	}

	dst, err := textconv.NewWriter(os.Stdout, *to, n)
	if err != nil {
		return err
	}

	if _, err := io.Copy(dst, src); err != nil {
		return err
	}
	return dst.Close()
}

func openInput(path string) (io.ReadCloser, error) {
	if path == "" || path == "-" {
		return io.NopCloser(os.Stdin), nil
	}
	return os.Open(path)
}

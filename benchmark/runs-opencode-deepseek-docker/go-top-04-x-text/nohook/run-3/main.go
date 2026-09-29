package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"example.com/textconv/internal/textconv"
)

func main() {
	var (
		from = flag.String("from", "utf-8", "source charset (IANA name)")
		to   = flag.String("to", "utf-8", "target charset (IANA name)")
		form = flag.String("form", "NFC", "Unicode normalization form: NFC, NFD, NFKC or NFKD (empty to skip)")
	)
	flag.Usage = func() {
		out := flag.CommandLine.Output()
		fmt.Fprintf(out, "Usage: %s [flags] [text]\n\n", os.Args[0])
		fmt.Fprintln(out, "Convert text between encodings and normalize Unicode.")
		fmt.Fprintln(out, "If no text argument is given, text is read from stdin.")
		fmt.Fprintln(out)
		fmt.Fprintln(out, "Flags:")
		flag.PrintDefaults()
	}
	flag.Parse()

	var raw []byte
	if flag.NArg() > 0 {
		raw = []byte(flag.Arg(0))
	} else {
		b, err := io.ReadAll(os.Stdin)
		if err != nil {
			fatal(err)
		}
		raw = b
	}

	utf8, err := textconv.Convert(raw, *from, "utf-8")
	if err != nil {
		fatal(err)
	}

	out := string(utf8)
	if *form != "" {
		f, err := textconv.ParseForm(*form)
		if err != nil {
			fatal(err)
		}
		out = textconv.Normalize(out, f)
	}

	final, err := textconv.Convert([]byte(out), "utf-8", *to)
	if err != nil {
		fatal(err)
	}

	if _, err := os.Stdout.Write(final); err != nil {
		fatal(err)
	}
}

func fatal(err error) {
	fmt.Fprintln(os.Stderr, "textconv:", err)
	os.Exit(1)
}

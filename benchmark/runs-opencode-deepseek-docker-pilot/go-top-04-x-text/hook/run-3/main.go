package main

import (
	"flag"
	"fmt"
	"io"
	"os"
	"sort"
)

// commonEncodings is shown by the -list flag. Any IANA/WHATWG label is
// accepted by -from and -to, this is only a convenience index.
var commonEncodings = []string{
	"utf-8", "utf-16le", "utf-16be",
	"iso-8859-1", "iso-8859-2", "iso-8859-5", "iso-8859-15",
	"windows-1250", "windows-1251", "windows-1252",
	"koi8-r", "koi8-u", "macintosh",
	"shift_jis", "euc-jp", "iso-2022-jp",
	"euc-kr", "gbk", "gb18030", "big5",
}

func main() {
	if err := run(os.Args[1:]); err != nil {
		fmt.Fprintln(os.Stderr, "textconv:", err)
		os.Exit(1)
	}
}

func run(args []string) error {
	fs := flag.NewFlagSet("textconv", flag.ContinueOnError)
	from := fs.String("from", "utf-8", "input encoding name (IANA/WHATWG label)")
	to := fs.String("to", "utf-8", "output encoding name (IANA/WHATWG label)")
	form := fs.String("normalize", "none", "Unicode normalization: none, nfc, nfd, nfkc or nfkd")
	in := fs.String("in", "-", "input file, or - for standard input")
	out := fs.String("out", "-", "output file, or - for standard output")
	list := fs.Bool("list", false, "list common encoding names and exit")
	if err := fs.Parse(args); err != nil {
		return err
	}

	if *list {
		names := append([]string(nil), commonEncodings...)
		sort.Strings(names)
		for _, name := range names {
			fmt.Println(name)
		}
		return nil
	}

	fromEnc, err := LookupEncoding(*from)
	if err != nil {
		return err
	}
	toEnc, err := LookupEncoding(*to)
	if err != nil {
		return err
	}
	nf, err := ParseForm(*form)
	if err != nil {
		return err
	}

	data, err := readAll(*in)
	if err != nil {
		return err
	}
	converted, err := Convert(data, fromEnc, toEnc, nf)
	if err != nil {
		return err
	}
	return writeAll(*out, converted)
}

func readAll(name string) ([]byte, error) {
	if name == "-" {
		return io.ReadAll(os.Stdin)
	}
	data, err := os.ReadFile(name)
	if err != nil {
		return nil, fmt.Errorf("reading %s: %w", name, err)
	}
	return data, nil
}

func writeAll(name string, data []byte) error {
	if name == "-" {
		_, err := os.Stdout.Write(data)
		return err
	}
	if err := os.WriteFile(name, data, 0o644); err != nil {
		return fmt.Errorf("writing %s: %w", name, err)
	}
	return nil
}

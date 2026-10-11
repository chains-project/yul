package main

import (
	"bytes"
	"testing"

	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/unicode/norm"
)

func TestRunDecodesLatin1(t *testing.T) {
	in := []byte{'c', 'a', 'f', 0xe9}
	var out bytes.Buffer
	if err := run(bytes.NewReader(in), &out, charmap.ISO8859_1, norm.NFC); err != nil {
		t.Fatal(err)
	}
	if want := "café"; out.String() != want {
		t.Fatalf("got %q, want %q", out.String(), want)
	}
}

func TestRunNormalizesToNFC(t *testing.T) {
	in := []byte("cafe\u0301")
	var out bytes.Buffer
	if err := run(bytes.NewReader(in), &out, nil, norm.NFC); err != nil {
		t.Fatal(err)
	}
	if want := "café"; out.String() != want {
		t.Fatalf("got %q, want %q", out.String(), want)
	}
}

func TestRunNormalizesToNFKD(t *testing.T) {
	in := []byte("ﬁ")
	var out bytes.Buffer
	if err := run(bytes.NewReader(in), &out, nil, norm.NFKD); err != nil {
		t.Fatal(err)
	}
	if want := "fi"; out.String() != want {
		t.Fatalf("got %q, want %q", out.String(), want)
	}
}

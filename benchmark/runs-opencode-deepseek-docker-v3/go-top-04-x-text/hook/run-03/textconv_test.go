package textconv

import (
	"bytes"
	"io"
	"testing"

	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/encoding/japanese"
	"golang.org/x/text/unicode/norm"
)

func TestLookup(t *testing.T) {
	if _, ok := Lookup("Shift_JIS"); !ok {
		t.Fatal("expected Shift_JIS to be registered")
	}
	if _, ok := Lookup("  UTF-8  "); !ok {
		t.Fatal("expected whitespace and case to be ignored")
	}
	if _, ok := Lookup("no-such-encoding"); ok {
		t.Fatal("expected unknown encoding to be missing")
	}
}

func TestDecodeLatin1(t *testing.T) {
	got, err := DecodeString([]byte{'c', 'a', 'f', 0xE9}, charmap.ISO8859_1)
	if err != nil {
		t.Fatal(err)
	}
	if want := "café"; got != want {
		t.Fatalf("got %q, want %q", got, want)
	}
}

func TestEncodeShiftJIS(t *testing.T) {
	const want = "こんにちは"
	encoded, err := Encode(want, japanese.ShiftJIS)
	if err != nil {
		t.Fatal(err)
	}
	decoded, err := DecodeString(encoded, japanese.ShiftJIS)
	if err != nil {
		t.Fatal(err)
	}
	if decoded != want {
		t.Fatalf("round trip got %q, want %q", decoded, want)
	}
}

func TestNilEncoding(t *testing.T) {
	if _, err := Decode(nil, nil); err == nil {
		t.Fatal("expected error for nil encoding")
	}
	if _, err := Encode("x", nil); err == nil {
		t.Fatal("expected error for nil encoding")
	}
}

func TestNormalize(t *testing.T) {
	decomposed := "e\u0301"
	if got := ToNFC(decomposed); got != "\u00e9" {
		t.Fatalf("NFC got %q", got)
	}
	if got := ToNFD("\u00e9"); got != decomposed {
		t.Fatalf("NFD got %q", got)
	}
	if got := ToNFKC("\u2460"); got != "1" {
		t.Fatalf("NFKC got %q", got)
	}
	if got := ToNFKD("\ufb01"); got != "fi" {
		t.Fatalf("NFKD got %q", got)
	}
}

func TestIsNormalized(t *testing.T) {
	if !IsNormalized("\u00e9", norm.NFC) {
		t.Fatal("expected composed form to be NFC")
	}
	if IsNormalized("e\u0301", norm.NFC) {
		t.Fatal("expected decomposed form not to be NFC")
	}
}

func TestNormalizeReader(t *testing.T) {
	r := NormalizeReader(bytes.NewReader([]byte("e\u0301")), norm.NFC)
	got, err := io.ReadAll(r)
	if err != nil {
		t.Fatal(err)
	}
	if string(got) != "\u00e9" {
		t.Fatalf("got %q", got)
	}
}

func TestConvert(t *testing.T) {
	got, err := Convert([]byte{'c', 'a', 'f', 0xE9}, charmap.ISO8859_1, norm.NFC)
	if err != nil {
		t.Fatal(err)
	}
	if want := []byte("café"); !bytes.Equal(got, want) {
		t.Fatalf("got %q, want %q", got, want)
	}
}

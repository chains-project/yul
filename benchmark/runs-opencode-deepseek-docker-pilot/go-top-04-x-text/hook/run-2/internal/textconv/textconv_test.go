package textconv

import (
	"testing"

	"golang.org/x/text/unicode/norm"
)

func TestDecodeWindows1252(t *testing.T) {
	// "Café" encoded as windows-1252 (0xE9 is é).
	src := []byte{0x43, 0x61, 0x66, 0xE9}
	got, err := Decode("windows-1252", src)
	if err != nil {
		t.Fatalf("Decode: %v", err)
	}
	if want := "Café"; string(got) != want {
		t.Fatalf("Decode = %q, want %q", got, want)
	}
}

func TestEncodeRoundTrip(t *testing.T) {
	want := []byte{0x43, 0x61, 0x66, 0xE9}
	enc, err := Encode("windows-1252", []byte("Café"))
	if err != nil {
		t.Fatalf("Encode: %v", err)
	}
	if string(enc) != string(want) {
		t.Fatalf("Encode = % x, want % x", enc, want)
	}
}

func TestDecodeUnknownEncoding(t *testing.T) {
	if _, err := Decode("not-a-real-encoding", []byte("x")); err == nil {
		t.Fatal("Decode: expected error for unknown encoding")
	}
}

func TestNormalize(t *testing.T) {
	// U+00E9 (é) decomposed is U+0065 U+0301 (e + combining acute).
	decomposed := "e\u0301"
	if IsNormal(norm.NFC, decomposed) {
		t.Fatal("decomposed string unexpectedly reports as NFC")
	}
	composed := Normalize(norm.NFC, decomposed)
	if composed != "\u00e9" {
		t.Fatalf("Normalize(NFC) = %q, want %q", composed, "\u00e9")
	}
	if !IsNormal(norm.NFC, composed) {
		t.Fatal("composed string should report as NFC")
	}
}

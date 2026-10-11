package textconv

import (
	"bytes"
	"testing"

	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/encoding/unicode"
	"golang.org/x/text/unicode/norm"
)

func TestLookupKnown(t *testing.T) {
	for _, name := range []string{"utf-8", "windows-1252", "iso-8859-1", "shift_jis"} {
		if _, err := Lookup(name); err != nil {
			t.Errorf("Lookup(%q) returned error: %v", name, err)
		}
	}
}

func TestLookupUnknown(t *testing.T) {
	if _, err := Lookup("not-a-real-encoding"); err == nil {
		t.Fatal("Lookup of unknown encoding should fail")
	}
}

func TestDecodeWindows1252(t *testing.T) {
	// 0x93/0x94 are curly double quotes in Windows-1252.
	got, err := Decode([]byte{0x93, 'h', 'i', 0x94}, charmap.Windows1252)
	if err != nil {
		t.Fatal(err)
	}
	if want := "\u201chi\u201d"; got != want {
		t.Fatalf("Decode = %q, want %q", got, want)
	}
}

func TestTranscodeRoundTrip(t *testing.T) {
	original := "café — naïve"
	encoded, err := Encode(original, charmap.Windows1252)
	if err != nil {
		t.Fatal(err)
	}
	decoded, err := Decode(encoded, charmap.Windows1252)
	if err != nil {
		t.Fatal(err)
	}
	if decoded != original {
		t.Fatalf("round trip = %q, want %q", decoded, original)
	}
}

func TestConvertNormalizes(t *testing.T) {
	// U+0065 U+0301 (e + combining acute) should compose to U+00E9.
	input := "e\u0301"
	got, err := Convert([]byte(input), unicode.UTF8, norm.NFC)
	if err != nil {
		t.Fatal(err)
	}
	if want := "\u00e9"; got != want {
		t.Fatalf("Convert NFC = %q, want %q", got, want)
	}
}

func TestNormalizeForms(t *testing.T) {
	const decomposed = "A\u030A" // A + combining ring above
	if got, want := NFC(decomposed), "\u00c5"; got != want {
		t.Errorf("NFC = %q, want %q", got, want)
	}
	if got := NFD("\u00c5"); got != decomposed {
		t.Errorf("NFD = %q, want %q", got, decomposed)
	}
	if got, want := NFKC("\ufb01"), "fi"; got != want {
		t.Errorf("NFKC ligature = %q, want %q", got, want)
	}
	if got, want := NFKD("\u00b2"), "2"; got != want {
		t.Errorf("NFKD superscript = %q, want %q", got, want)
	}
}

func TestTranscode(t *testing.T) {
	got, err := Transcode([]byte{0x93, 'x', 0x94}, charmap.Windows1252, unicode.UTF8)
	if err != nil {
		t.Fatal(err)
	}
	if want := []byte("\u201cx\u201d"); !bytes.Equal(got, want) {
		t.Fatalf("Transcode = %q, want %q", got, want)
	}
}

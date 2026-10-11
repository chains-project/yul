package textcodec

import (
	"bytes"
	"testing"

	"golang.org/x/text/encoding"
	"golang.org/x/text/unicode/norm"
)

func TestLookupEncoding(t *testing.T) {
	nop, err := LookupEncoding("UTF-8")
	if err != nil {
		t.Fatalf("LookupEncoding(utf-8): %v", err)
	}
	if nop != encoding.Nop {
		t.Fatalf("utf-8: got %v, want encoding.Nop", nop)
	}

	if _, err := LookupEncoding("windows-1252"); err != nil {
		t.Fatalf("LookupEncoding(windows-1252): %v", err)
	}
	if _, err := LookupEncoding("not-a-charset"); err == nil {
		t.Fatal("LookupEncoding(not-a-charset): want error, got nil")
	}
}

func TestDecodeWindows1252(t *testing.T) {
	// 0x93 is a left double quotation mark in Windows-1252.
	got, err := Decode([]byte{0x93}, mustEncoding(t, "windows-1252"))
	if err != nil {
		t.Fatalf("Decode: %v", err)
	}
	if want := "\u201c"; string(got) != want {
		t.Fatalf("Decode = %q, want %q", got, want)
	}
}

func TestConvertRoundTrip(t *testing.T) {
	enc := mustEncoding(t, "windows-1252")
	utf8 := []byte("caf\u00e9 \u2014 na\u00efve")

	encoded, err := Encode(utf8, enc)
	if err != nil {
		t.Fatalf("Encode: %v", err)
	}
	if bytes.Equal(encoded, utf8) {
		t.Fatal("Encode produced UTF-8 unchanged for a non-UTF-8 target")
	}

	decoded, err := Decode(encoded, enc)
	if err != nil {
		t.Fatalf("Decode: %v", err)
	}
	if !bytes.Equal(decoded, utf8) {
		t.Fatalf("round trip = %q, want %q", decoded, utf8)
	}
}

func TestConvertShiftJIS(t *testing.T) {
	from, _ := LookupEncoding("shift_jis")
	to, _ := LookupEncoding("utf-8")

	src := []byte{0x82, 0xb1, 0x82, 0xf1, 0x82, 0xc9, 0x82, 0xbf, 0x82, 0xcd} // こんにちは
	got, err := Convert(src, from, to)
	if err != nil {
		t.Fatalf("Convert: %v", err)
	}
	if want := "こんにちは"; string(got) != want {
		t.Fatalf("Convert = %q, want %q", got, want)
	}
}

func TestLookupFormAndNormalize(t *testing.T) {
	tests := []struct {
		form string
		in   string
		want string
	}{
		{"NFC", "e\u0301", "\u00e9"},
		{"NFD", "\u00e9", "e\u0301"},
		{"NFKC", "\u2460", "1"},
		{"nfkd", "\ufb01", "fi"},
	}
	for _, tt := range tests {
		form, err := LookupForm(tt.form)
		if err != nil {
			t.Fatalf("LookupForm(%q): %v", tt.form, err)
		}
		if got := Normalize(tt.in, &form); got != tt.want {
			t.Errorf("%s(%q) = %q, want %q", tt.form, tt.in, got, tt.want)
		}
	}

	if got := Normalize("e\u0301", nil); got != "\u00e9" {
		t.Errorf("Normalize default = %q, want NFC", got)
	}
	if _, err := LookupForm("nfxx"); err == nil {
		t.Fatal("LookupForm(nfxx): want error, got nil")
	}
}

func TestIsNormalized(t *testing.T) {
	if !IsNormalized("\u00e9", norm.NFC) {
		t.Error("U+00E9 should be NFC")
	}
	if IsNormalized("e\u0301", norm.NFC) {
		t.Error("e + combining acute should not be NFC")
	}
}

func mustEncoding(t *testing.T, name string) encoding.Encoding {
	t.Helper()
	enc, err := LookupEncoding(name)
	if err != nil {
		t.Fatalf("LookupEncoding(%q): %v", name, err)
	}
	return enc
}

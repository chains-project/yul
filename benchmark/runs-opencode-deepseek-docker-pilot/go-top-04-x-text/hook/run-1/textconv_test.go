package textconv

import (
	"bytes"
	"io"
	"strings"
	"testing"

	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/encoding/japanese"
)

func TestNormalize(t *testing.T) {
	const (
		composed   = "\u00e9"  // é
		decomposed = "e\u0301" // e + combining acute
		fullWidth  = "\uff21"  // Ａ
		circledOne = "\u2460"  // ①
	)

	tests := []struct {
		name string
		in   string
		form Form
		want string
	}{
		{"nfc composes", decomposed, NFC, composed},
		{"nfd decomposes", composed, NFD, decomposed},
		{"nfkc folds width", fullWidth, NFKC, "A"},
		{"nfkc folds compatibility", circledOne, NFKC, "1"},
		{"nfkd folds and decomposes", "\u00e9", NFKD, decomposed},
		{"none is a no-op", decomposed, None, decomposed},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := Normalize(tt.in, tt.form); got != tt.want {
				t.Errorf("Normalize(%q, %v) = %q, want %q", tt.in, tt.form, got, tt.want)
			}
		})
	}
}

func TestIsNormalized(t *testing.T) {
	if !IsNormalized("\u00e9", NFC) {
		t.Error("é should be NFC-normalized")
	}
	if IsNormalized("e\u0301", NFC) {
		t.Error("e+combining acute should not be NFC-normalized")
	}
	if !IsNormalized("e\u0301", NFD) {
		t.Error("e+combining acute should be NFD-normalized")
	}
}

func TestParseForm(t *testing.T) {
	cases := map[string]Form{
		"nfc":    NFC,
		"NFD":    NFD,
		"nfKc":   NFKC,
		"":       None,
		" none ": None,
	}
	for name, want := range cases {
		got, ok := ParseForm(name)
		if !ok || got != want {
			t.Errorf("ParseForm(%q) = (%v, %v), want (%v, true)", name, got, ok, want)
		}
	}
	if _, ok := ParseForm("nfx"); ok {
		t.Error("ParseForm(\"nfx\") should not be ok")
	}
}

func TestDecodeLatin1(t *testing.T) {
	got, err := Decode([]byte{'e', 0xe9}, charmap.ISO8859_1)
	if err != nil {
		t.Fatal(err)
	}
	if got != "e\u00e9" {
		t.Errorf("Decode = %q, want %q", got, "e\u00e9")
	}
}

func TestEncodeLatin1(t *testing.T) {
	got, err := Encode("e\u00e9", charmap.ISO8859_1)
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(got, []byte{'e', 0xe9}) {
		t.Errorf("Encode = % x, want 65 e9", got)
	}
}

func TestEncodeUnrepresentableErrors(t *testing.T) {
	if _, err := Encode("\u65e5", charmap.ISO8859_1); err == nil {
		t.Error("encoding Japanese to ISO-8859-1 should fail")
	}
}

func TestShiftJISRoundTrip(t *testing.T) {
	const text = "日本語"
	encoded, err := Encode(text, japanese.ShiftJIS)
	if err != nil {
		t.Fatal(err)
	}
	decoded, err := Decode(encoded, japanese.ShiftJIS)
	if err != nil {
		t.Fatal(err)
	}
	if decoded != text {
		t.Errorf("round trip = %q, want %q", decoded, text)
	}
}

func TestConvertNormalizes(t *testing.T) {
	// Decomposed UTF-8 "é" normalized to NFC and re-encoded as UTF-8.
	got, err := Convert([]byte("e\u0301"), nil, nil, NFC)
	if err != nil {
		t.Fatal(err)
	}
	if string(got) != "\u00e9" {
		t.Errorf("Convert = %q, want %q", got, "\u00e9")
	}
}

func TestConvertBetweenEncodings(t *testing.T) {
	// ISO-8859-1 "eé" to UTF-8.
	got, err := Convert([]byte{'e', 0xe9}, charmap.ISO8859_1, nil, NFC)
	if err != nil {
		t.Fatal(err)
	}
	if string(got) != "e\u00e9" {
		t.Errorf("Convert = %q, want %q", got, "e\u00e9")
	}
}

func TestLookup(t *testing.T) {
	for _, name := range []string{"UTF-8", "utf8", "Shift_JIS", "sjis", "Latin1", "cp1252"} {
		if _, ok := Lookup(name); !ok {
			t.Errorf("Lookup(%q) failed", name)
		}
	}
	if _, ok := Lookup("not-an-encoding"); ok {
		t.Error("Lookup of unknown encoding should fail")
	}
}

func TestEncodingsSorted(t *testing.T) {
	names := Encodings()
	if len(names) == 0 {
		t.Fatal("Encodings returned nothing")
	}
	for i := 1; i < len(names); i++ {
		if names[i-1] >= names[i] {
			t.Fatalf("Encodings not sorted: %q >= %q", names[i-1], names[i])
		}
	}
}

func TestReaderWriter(t *testing.T) {
	r := NewReader(strings.NewReader("e\xe9"), charmap.ISO8859_1, NFC)
	got, err := io.ReadAll(r)
	if err != nil {
		t.Fatal(err)
	}
	if string(got) != "e\u00e9" {
		t.Errorf("NewReader = %q, want %q", got, "e\u00e9")
	}

	var buf bytes.Buffer
	w := NewWriter(&buf, charmap.ISO8859_1)
	if _, err := io.WriteString(w, "e\u00e9"); err != nil {
		t.Fatal(err)
	}
	if err := w.Close(); err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(buf.Bytes(), []byte{'e', 0xe9}) {
		t.Errorf("NewWriter = % x, want 65 e9", buf.Bytes())
	}
}

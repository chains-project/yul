package textconv

import (
	"bytes"
	"io"
	"strings"
	"testing"
)

func TestLookup(t *testing.T) {
	want, err := Lookup("utf-8")
	if err != nil {
		t.Fatalf("Lookup(utf-8): %v", err)
	}
	for _, name := range []string{"UTF_8", "utf8", "  Utf-8  "} {
		got, err := Lookup(name)
		if err != nil {
			t.Errorf("Lookup(%q): %v", name, err)
			continue
		}
		if got != want {
			t.Errorf("Lookup(%q) != Lookup(utf-8)", name)
		}
	}
	if _, err := Lookup("no-such-encoding"); err == nil {
		t.Error("Lookup(no-such-encoding) succeeded, want error")
	}
}

func TestNamesSorted(t *testing.T) {
	names := Names()
	if len(names) == 0 {
		t.Fatal("Names returned nothing")
	}
	for i := 1; i < len(names); i++ {
		if names[i-1] >= names[i] {
			t.Fatalf("Names not sorted: %q before %q", names[i-1], names[i])
		}
	}
}

func TestDecode(t *testing.T) {
	// 0x80 is the euro sign in Windows-1252.
	got, err := Decode([]byte{0x80}, "windows-1252")
	if err != nil {
		t.Fatalf("Decode: %v", err)
	}
	if want := "\u20ac"; string(got) != want {
		t.Errorf("Decode = %q, want %q", got, want)
	}
}

func TestEncode(t *testing.T) {
	got, err := Encode([]byte("café"), "iso-8859-1")
	if err != nil {
		t.Fatalf("Encode: %v", err)
	}
	if want := []byte{'c', 'a', 'f', 0xe9}; !bytes.Equal(got, want) {
		t.Errorf("Encode = % x, want % x", got, want)
	}
}

func TestConvert(t *testing.T) {
	// NFD "e" + combining acute, supplied as UTF-8, composed to NFC.
	got, err := Convert([]byte("e\u0301"), "utf-8", "utf-8", NFC)
	if err != nil {
		t.Fatalf("Convert: %v", err)
	}
	if want := "\u00e9"; string(got) != want {
		t.Errorf("Convert = %q, want %q", got, want)
	}
}

func TestNormalize(t *testing.T) {
	tests := []struct {
		name string
		in   string
		form Normalization
		want string
	}{
		{"none keeps input", "e\u0301", None, "e\u0301"},
		{"nfc composes", "e\u0301", NFC, "\u00e9"},
		{"nfd decomposes", "\u00e9", NFD, "e\u0301"},
		{"nfkc composes", "\u00e9", NFKC, "\u00e9"},
		{"nfkc folds ligature", "\ufb01", NFKC, "fi"},
		{"nfkd folds circled digit", "\u2460", NFKD, "1"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := Normalize(tt.in, tt.form); got != tt.want {
				t.Errorf("Normalize(%q, %s) = %q, want %q", tt.in, tt.form, got, tt.want)
			}
		})
	}
}

func TestParseNormalization(t *testing.T) {
	for in, want := range map[string]Normalization{
		"":     None,
		"nfc":  NFC,
		" NFD": NFD,
		"nfkc": NFKC,
		"NFKD": NFKD,
	} {
		got, err := ParseNormalization(in)
		if err != nil {
			t.Errorf("ParseNormalization(%q): %v", in, err)
			continue
		}
		if got != want {
			t.Errorf("ParseNormalization(%q) = %q, want %q", in, got, want)
		}
	}
	if _, err := ParseNormalization("NFX"); err == nil {
		t.Error("ParseNormalization(NFX) succeeded, want error")
	}
}

func TestStreamRoundTrip(t *testing.T) {
	const text = "Grüße aus Köln — こんにちは"

	encoded, err := Encode([]byte(text), "windows-1252")
	if err != nil {
		t.Fatalf("Encode: %v", err)
	}

	r, err := NewReader(bytes.NewReader(encoded), "windows-1252")
	if err != nil {
		t.Fatalf("NewReader: %v", err)
	}

	var buf bytes.Buffer
	w, err := NewWriter(&buf, "utf-8", None)
	if err != nil {
		t.Fatalf("NewWriter: %v", err)
	}
	if _, err := io.Copy(w, r); err != nil {
		t.Fatalf("copy: %v", err)
	}
	if err := w.Close(); err != nil {
		t.Fatalf("Close: %v", err)
	}
	if got := buf.String(); !strings.Contains(got, "Grüße") {
		t.Errorf("round trip lost data: %q", got)
	}
}

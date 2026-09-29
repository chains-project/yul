package main

import "testing"

func TestConvertWindows1252ToUTF8(t *testing.T) {
	from, err := LookupEncoding("windows-1252")
	if err != nil {
		t.Fatal(err)
	}
	got, err := Convert([]byte{0xE9}, from, nil, nil)
	if err != nil {
		t.Fatal(err)
	}
	if string(got) != "é" {
		t.Fatalf("Convert = %q, want %q", got, "é")
	}
}

func TestConvertUTF8ToUTF16LE(t *testing.T) {
	to, err := LookupEncoding("utf-16le")
	if err != nil {
		t.Fatal(err)
	}
	got, err := Convert([]byte("hi"), nil, to, nil)
	if err != nil {
		t.Fatal(err)
	}
	want := []byte{0x68, 0x00, 0x69, 0x00}
	if string(got) != string(want) {
		t.Fatalf("Convert = % x, want % x", got, want)
	}
}

func TestNormalizeNFD(t *testing.T) {
	nf, err := ParseForm("nfd")
	if err != nil {
		t.Fatal(err)
	}
	// U+00C5 decomposes to U+0041 U+030A.
	if got, want := Normalize("\u00C5", nf), "A\u030A"; got != want {
		t.Fatalf("Normalize = %q, want %q", got, want)
	}
}

func TestNormalizeNFC(t *testing.T) {
	nf, err := ParseForm("nfc")
	if err != nil {
		t.Fatal(err)
	}
	if got, want := Normalize("A\u030A", nf), "\u00C5"; got != want {
		t.Fatalf("Normalize = %q, want %q", got, want)
	}
}

func TestEncodeDecodeRoundTripShiftJIS(t *testing.T) {
	sjis, err := LookupEncoding("shift_jis")
	if err != nil {
		t.Fatal(err)
	}
	const want = "日本語"
	encoded, err := Encode(want, sjis)
	if err != nil {
		t.Fatal(err)
	}
	got, err := Decode(encoded, sjis)
	if err != nil {
		t.Fatal(err)
	}
	if got != want {
		t.Fatalf("round trip = %q, want %q", got, want)
	}
}

func TestParseFormNone(t *testing.T) {
	for _, name := range []string{"", "none", "NONE"} {
		nf, err := ParseForm(name)
		if err != nil {
			t.Fatalf("ParseForm(%q): %v", name, err)
		}
		if nf != nil {
			t.Fatalf("ParseForm(%q) = %v, want nil", name, nf)
		}
	}
}

func TestParseFormUnknown(t *testing.T) {
	if _, err := ParseForm("bogus"); err == nil {
		t.Fatal("ParseForm(bogus) = nil error, want error")
	}
}

func TestLookupEncodingUnknown(t *testing.T) {
	if _, err := LookupEncoding("definitely-not-an-encoding"); err == nil {
		t.Fatal("LookupEncoding = nil error, want error")
	}
}

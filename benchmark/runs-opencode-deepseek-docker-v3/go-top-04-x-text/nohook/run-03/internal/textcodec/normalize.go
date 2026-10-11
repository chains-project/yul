package textcodec

import (
	"fmt"
	"strings"

	"golang.org/x/text/unicode/norm"
)

// LookupForm parses a Unicode normalization form name. Recognized values are
// "NFC", "NFD", "NFKC" and "NFKD", case-insensitively. An empty name returns
// norm.NFC.
func LookupForm(name string) (norm.Form, error) {
	switch strings.ToUpper(strings.TrimSpace(name)) {
	case "", "NFC":
		return norm.NFC, nil
	case "NFD":
		return norm.NFD, nil
	case "NFKC":
		return norm.NFKC, nil
	case "NFKD":
		return norm.NFKD, nil
	default:
		return 0, fmt.Errorf("unknown normalization form %q", name)
	}
}

// Normalize returns s normalized to the given Unicode form. A nil form is
// treated as norm.NFC, the form recommended for interchange.
func Normalize(s string, form *norm.Form) string {
	if form == nil {
		return norm.NFC.String(s)
	}
	return form.String(s)
}

// IsNormalized reports whether s is already in the given normalization form.
func IsNormalized(s string, form norm.Form) bool {
	return form.IsNormalString(s)
}

package textconv

import (
	"fmt"
	"strings"

	"golang.org/x/text/unicode/norm"
)

// Form identifies a Unicode normalization form.
type Form int

const (
	NFC Form = iota
	NFD
	NFKC
	NFKD
)

// ParseForm parses a normalization form name (case-insensitive).
func ParseForm(s string) (Form, error) {
	switch strings.ToUpper(strings.TrimSpace(s)) {
	case "NFC":
		return NFC, nil
	case "NFD":
		return NFD, nil
	case "NFKC":
		return NFKC, nil
	case "NFKD":
		return NFKD, nil
	default:
		return 0, fmt.Errorf("textconv: unknown normalization form %q", s)
	}
}

func (f Form) String() string {
	switch f {
	case NFC:
		return "NFC"
	case NFD:
		return "NFD"
	case NFKC:
		return "NFKC"
	case NFKD:
		return "NFKD"
	default:
		return fmt.Sprintf("Form(%d)", int(f))
	}
}

func (f Form) norm() norm.Form {
	switch f {
	case NFD:
		return norm.NFD
	case NFKC:
		return norm.NFKC
	case NFKD:
		return norm.NFKD
	default:
		return norm.NFC
	}
}

// Normalize returns s converted to the given Unicode normalization form.
func Normalize(s string, f Form) string {
	return f.norm().String(s)
}

// IsNormalized reports whether s is already in the given normalization form.
func IsNormalized(s string, f Form) bool {
	return f.norm().IsNormalString(s)
}

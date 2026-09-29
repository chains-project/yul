package textconv

import (
	"fmt"
	"strings"

	"golang.org/x/text/unicode/norm"
)

// Normalization identifies a Unicode normalization form.
type Normalization string

const (
	// None disables normalization.
	None Normalization = ""
	// NFC is Unicode Normalization Form C (canonical composition).
	NFC Normalization = "NFC"
	// NFD is Unicode Normalization Form D (canonical decomposition).
	NFD Normalization = "NFD"
	// NFKC is Unicode Normalization Form KC (compatibility composition).
	NFKC Normalization = "NFKC"
	// NFKD is Unicode Normalization Form KD (compatibility decomposition).
	NFKD Normalization = "NFKD"
)

// ParseNormalization converts a case-insensitive form name such as "NFC" or
// "nfkd" into a Normalization. An empty name yields None.
func ParseNormalization(name string) (Normalization, error) {
	switch strings.ToUpper(strings.TrimSpace(name)) {
	case "":
		return None, nil
	case "NFC":
		return NFC, nil
	case "NFD":
		return NFD, nil
	case "NFKC":
		return NFKC, nil
	case "NFKD":
		return NFKD, nil
	default:
		return None, fmt.Errorf("textconv: unknown normalization form %q", name)
	}
}

// form maps a Normalization onto its norm.Form. None maps to NFC, which is
// harmless because callers check for None before normalizing.
func (n Normalization) form() norm.Form {
	switch n {
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

// Normalize returns s normalized to form n. It returns s unchanged when n is
// None.
func Normalize(s string, n Normalization) string {
	if n == None {
		return s
	}
	return n.form().String(s)
}

package pypi

import "strings"

// normalizePackageName applies PEP 503 normalization so that e.g.
// "My-Package_Name" and "my.package.name" are recognized as the same
// distribution.
func normalizePackageName(name string) string {
	name = strings.ToLower(name)
	var b strings.Builder
	prevSep := false
	for _, r := range name {
		if r == '-' || r == '_' || r == '.' {
			if !prevSep {
				b.WriteByte('-')
			}
			prevSep = true
			continue
		}
		b.WriteRune(r)
		prevSep = false
	}
	return strings.Trim(b.String(), "-")
}

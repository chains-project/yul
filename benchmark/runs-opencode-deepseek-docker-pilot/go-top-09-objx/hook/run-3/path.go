package mapq

import "strconv"

// segment is a single step in a parsed path. A segment is either a map key or
// a slice index.
type segment struct {
	key   string
	index int
	isIdx bool
}

// parsePath splits a path into segments. Paths use "." to separate map keys and
// "[n]" to address slice elements, e.g. "users[0].address.city". A backslash
// escapes the next character so keys containing "." or "[" can still be
// addressed, e.g. `a\.b` refers to the single key "a.b".
func parsePath(path string) []segment {
	if path == "" {
		return nil
	}

	runes := []rune(path)
	segs := make([]segment, 0, 4)
	var key []rune

	flushKey := func() {
		if len(key) > 0 {
			segs = append(segs, segment{key: string(key)})
			key = key[:0]
		}
	}

	for i := 0; i < len(runes); i++ {
		switch c := runes[i]; c {
		case '\\':
			if i+1 < len(runes) {
				i++
				key = append(key, runes[i])
			}
		case '.':
			flushKey()
		case '[':
			flushKey()
			end := i + 1
			for end < len(runes) && runes[end] != ']' {
				end++
			}
			if end == len(runes) {
				// Unterminated index: treat the remainder as a literal key.
				key = append(key, runes[i:]...)
				i = len(runes)
				break
			}
			if n, err := strconv.Atoi(string(runes[i+1 : end])); err == nil && n >= 0 {
				segs = append(segs, segment{index: n, isIdx: true})
			}
			i = end
		default:
			key = append(key, c)
		}
	}
	flushKey()
	return segs
}

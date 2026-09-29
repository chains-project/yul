// Package mapq provides a fluent, chainable API for reading and mutating
// arbitrary map[string]interface{} data, such as the result of decoding JSON
// with encoding/json.
//
// Values are addressed by a compact path expression that supports nested maps
// and slices using either dotted or bracketed syntax:
//
//	user.name
//	user.address.city
//	items[0].name
//	items.0.name
//	users[1]["first.name"]   // quoted key for keys containing dots
//
// A numeric segment addresses a slice element; wrap it in quotes to address a
// numeric map key literally (for example ["0"]). The zero value is not usable;
// construct a Map with New, Wrap or FromJSON.
package mapq

import (
	"fmt"
	"strconv"
	"strings"
)

// token is a single step of a parsed path. Exactly one of key or index is
// meaningful, selected by isIndex.
type token struct {
	key     string
	index   int
	isIndex bool
}

// parsePath converts a path expression into a sequence of tokens. An empty
// path yields no tokens, which addresses the root map itself.
func parsePath(path string) ([]token, error) {
	var tokens []token
	var buf strings.Builder
	lastWasDot := false

	appendSegment := func(segment string, quoted bool) error {
		if segment == "" {
			return nil
		}
		if !quoted {
			if idx, ok := parseIndex(segment); ok {
				if idx < 0 {
					return fmt.Errorf("mapq: negative index in path %q", path)
				}
				tokens = append(tokens, token{index: idx, isIndex: true})
				return nil
			}
		}
		tokens = append(tokens, token{key: segment})
		return nil
	}

	runes := []rune(path)
	for i := 0; i < len(runes); i++ {
		switch r := runes[i]; r {
		case '.':
			if err := appendSegment(buf.String(), false); err != nil {
				return nil, err
			}
			buf.Reset()
			if lastWasDot {
				return nil, fmt.Errorf("mapq: empty segment in path %q", path)
			}
			lastWasDot = true
		case '[':
			if err := appendSegment(buf.String(), false); err != nil {
				return nil, err
			}
			buf.Reset()
			lastWasDot = false
			segment, next, quoted, err := scanBracket(runes, i+1, path)
			if err != nil {
				return nil, err
			}
			i = next
			if segment == "" {
				return nil, fmt.Errorf("mapq: empty index in path %q", path)
			}
			if err := appendSegment(segment, quoted); err != nil {
				return nil, err
			}
		default:
			buf.WriteRune(r)
			lastWasDot = false
		}
	}
	if err := appendSegment(buf.String(), false); err != nil {
		return nil, err
	}
	return tokens, nil
}

// parseIndex reports whether segment is an optionally-signed decimal integer
// and returns its value.
func parseIndex(segment string) (int, bool) {
	body := segment
	if body != "" && (body[0] == '-' || body[0] == '+') {
		body = body[1:]
	}
	if body == "" {
		return 0, false
	}
	for _, r := range body {
		if r < '0' || r > '9' {
			return 0, false
		}
	}
	n, err := strconv.Atoi(segment)
	if err != nil {
		return 0, false
	}
	return n, true
}

// scanBracket reads the contents of a bracket expression beginning at start
// (the index immediately after '['). It returns the unescaped segment, the
// index of the closing ']', and whether the segment was explicitly quoted.
func scanBracket(runes []rune, start int, path string) (segment string, closeIdx int, quoted bool, err error) {
	var sb strings.Builder
	inQuote := false
	var quote rune

	for i := start; i < len(runes); i++ {
		switch c := runes[i]; {
		case inQuote:
			if c == '\\' && i+1 < len(runes) {
				i++
				sb.WriteRune(runes[i])
				continue
			}
			if c == quote {
				inQuote = false
				continue
			}
			sb.WriteRune(c)
		case c == '"' || c == '\'':
			inQuote = true
			quoted = true
			quote = c
		case c == ']':
			return strings.TrimSpace(sb.String()), i, quoted, nil
		default:
			sb.WriteRune(c)
		}
	}
	return "", 0, false, fmt.Errorf("mapq: unclosed '[' in path %q", path)
}

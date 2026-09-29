package dynmap

import (
	"fmt"
	"strconv"
	"strings"
)

type tokenKind uint8

const (
	keyToken tokenKind = iota
	indexToken
)

type token struct {
	kind  tokenKind
	key   string
	index int
}

// parsePath splits a dotted path into key and index tokens. Slice
// indices are written as [n], for example "users[0].name". An empty path
// yields no tokens and addresses the root map.
func parsePath(path string) ([]token, error) {
	if path == "" {
		return nil, nil
	}
	var toks []token
	var key strings.Builder
	flush := func() {
		if key.Len() > 0 {
			toks = append(toks, token{kind: keyToken, key: key.String()})
			key.Reset()
		}
	}
	for i := 0; i < len(path); {
		switch c := path[i]; c {
		case '.':
			flush()
			i++
		case '[':
			flush()
			end := strings.IndexByte(path[i:], ']')
			if end < 0 {
				return nil, fmt.Errorf("dynmap: path %q has an unmatched '['", path)
			}
			raw := strings.TrimSpace(path[i+1 : i+end])
			idx, err := strconv.Atoi(raw)
			if err != nil || idx < 0 {
				return nil, fmt.Errorf("dynmap: path %q has an invalid index %q", path, raw)
			}
			toks = append(toks, token{kind: indexToken, index: idx})
			i += end + 1
		default:
			key.WriteByte(c)
			i++
		}
	}
	flush()
	return toks, nil
}

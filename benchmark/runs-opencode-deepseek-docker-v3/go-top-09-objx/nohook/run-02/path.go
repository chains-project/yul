package fluentmap

import (
	"strconv"
	"strings"
)

type pathToken struct {
	key     string
	index   int
	isIndex bool
}

// parsePath splits a path such as "user.tags[0].name" into tokens.
func parsePath(path string) ([]pathToken, bool) {
	if path == "" {
		return nil, false
	}
	var tokens []pathToken
	for _, part := range strings.Split(path, ".") {
		if part == "" {
			return nil, false
		}
		key := part
		rest := ""
		if i := strings.IndexByte(part, '['); i >= 0 {
			key, rest = part[:i], part[i:]
		}
		if key != "" {
			tokens = append(tokens, pathToken{key: key})
		} else if len(tokens) == 0 {
			return nil, false
		}
		for rest != "" {
			if rest[0] != '[' {
				return nil, false
			}
			end := strings.IndexByte(rest, ']')
			if end < 0 {
				return nil, false
			}
			idx, err := strconv.Atoi(rest[1:end])
			if err != nil || idx < 0 {
				return nil, false
			}
			tokens = append(tokens, pathToken{index: idx, isIndex: true})
			rest = rest[end+1:]
		}
	}
	return tokens, true
}

// GetPath returns the value at a dot/bracket path, e.g. "a.b[0].c".
func (m *Map) GetPath(path string) (interface{}, bool) {
	return m.lookupPath(path)
}

// HasPath reports whether a value exists at the given path.
func (m *Map) HasPath(path string) bool {
	_, ok := m.lookupPath(path)
	return ok
}

// SetPath assigns value at a dot/bracket path, creating intermediate maps and
// slices as needed, and returns the receiver for chaining.
func (m *Map) SetPath(path string, value interface{}) *Map {
	tokens, ok := parsePath(path)
	if !ok {
		return m
	}
	res, ok := setAt(m.data, tokens, value)
	if !ok {
		return m
	}
	if mp, ok := res.(map[string]interface{}); ok {
		m.data = mp
	}
	return m
}

// DeletePath removes the value at a dot/bracket path and returns the receiver.
// For slice elements, the element is removed and the slice shrinks.
func (m *Map) DeletePath(path string) *Map {
	tokens, ok := parsePath(path)
	if !ok {
		return m
	}
	if res, ok := deleteAt(m.data, tokens); ok {
		if mp, ok := res.(map[string]interface{}); ok {
			m.data = mp
		}
	}
	return m
}

func (m *Map) lookupPath(path string) (interface{}, bool) {
	tokens, ok := parsePath(path)
	if !ok {
		return nil, false
	}
	var cur interface{} = m.Value()
	for _, tok := range tokens {
		if tok.isIndex {
			slice, ok := cur.([]interface{})
			if !ok || tok.index >= len(slice) {
				return nil, false
			}
			cur = slice[tok.index]
			continue
		}
		mp, ok := cur.(map[string]interface{})
		if !ok {
			return nil, false
		}
		v, ok := mp[tok.key]
		if !ok {
			return nil, false
		}
		cur = v
	}
	return cur, true
}

// setAt walks tokens creating intermediate maps/slices. It returns the possibly
// new node so callers can assign it back into the parent.
func setAt(node interface{}, tokens []pathToken, value interface{}) (interface{}, bool) {
	if len(tokens) == 0 {
		return value, true
	}
	tok := tokens[0]
	if tok.isIndex {
		slice, _ := node.([]interface{})
		if node != nil {
			if _, ok := node.([]interface{}); !ok {
				return node, false
			}
		}
		for len(slice) <= tok.index {
			slice = append(slice, nil)
		}
		child, ok := setAt(slice[tok.index], tokens[1:], value)
		if !ok {
			return node, false
		}
		slice[tok.index] = child
		return slice, true
	}

	mp, _ := node.(map[string]interface{})
	if node != nil {
		if _, ok := node.(map[string]interface{}); !ok {
			return node, false
		}
	} else {
		mp = make(map[string]interface{})
	}
	child, ok := setAt(mp[tok.key], tokens[1:], value)
	if !ok {
		return node, false
	}
	mp[tok.key] = child
	return mp, true
}

func deleteAt(node interface{}, tokens []pathToken) (interface{}, bool) {
	if len(tokens) == 0 {
		return node, false
	}
	tok := tokens[0]
	if len(tokens) == 1 {
		if tok.isIndex {
			slice, ok := node.([]interface{})
			if !ok || tok.index >= len(slice) {
				return node, false
			}
			slice = append(slice[:tok.index], slice[tok.index+1:]...)
			return slice, true
		}
		mp, ok := node.(map[string]interface{})
		if !ok {
			return node, false
		}
		if _, exists := mp[tok.key]; !exists {
			return node, false
		}
		delete(mp, tok.key)
		return mp, true
	}

	if tok.isIndex {
		slice, ok := node.([]interface{})
		if !ok || tok.index >= len(slice) {
			return node, false
		}
		child, ok := deleteAt(slice[tok.index], tokens[1:])
		if !ok {
			return node, false
		}
		slice[tok.index] = child
		return slice, true
	}

	mp, ok := node.(map[string]interface{})
	if !ok {
		return node, false
	}
	child, ok := deleteAt(mp[tok.key], tokens[1:])
	if !ok {
		return node, false
	}
	mp[tok.key] = child
	return mp, true
}

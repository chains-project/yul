package mapx

import (
	"fmt"
	"strconv"
	"strings"
)

type segment struct {
	key     string
	index   int
	isIndex bool
}

func parsePath(path string) ([]segment, error) {
	if path == "" {
		return nil, fmt.Errorf("%w: empty path", ErrInvalidPath)
	}

	var segs []segment
	for i := 0; i < len(path); {
		if path[i] == '[' {
			end := strings.IndexByte(path[i:], ']')
			if end < 0 {
				return nil, fmt.Errorf("%w: unclosed '[' in %q", ErrInvalidPath, path)
			}
			digits := path[i+1 : i+end]
			n, err := strconv.Atoi(digits)
			if err != nil || n < 0 {
				return nil, fmt.Errorf("%w: bad index %q", ErrInvalidPath, digits)
			}
			segs = append(segs, segment{index: n, isIndex: true})
			i += end + 1
		} else {
			start := i
			for i < len(path) && path[i] != '.' && path[i] != '[' {
				i++
			}
			if start == i {
				return nil, fmt.Errorf("%w: empty key in %q", ErrInvalidPath, path)
			}
			segs = append(segs, segment{key: path[start:i]})
		}

		if i < len(path) && path[i] == '.' {
			i++
			if i == len(path) {
				return nil, fmt.Errorf("%w: trailing '.' in %q", ErrInvalidPath, path)
			}
		}
	}
	return segs, nil
}

type mapRef interface {
	set(key string, value interface{})
	lookup(key string) (interface{}, bool)
	remove(key string)
}

type stdMap map[string]interface{}

func (m stdMap) set(key string, value interface{})     { m[key] = value }
func (m stdMap) lookup(key string) (interface{}, bool) { v, ok := m[key]; return v, ok }
func (m stdMap) remove(key string)                     { delete(m, key) }

type namedMap Map

func (m namedMap) set(key string, value interface{})     { m[key] = value }
func (m namedMap) lookup(key string) (interface{}, bool) { v, ok := m[key]; return v, ok }
func (m namedMap) remove(key string)                     { delete(m, key) }

func asMapRef(v interface{}) (mapRef, bool) {
	switch m := v.(type) {
	case map[string]interface{}:
		return stdMap(m), true
	case Map:
		return namedMap(m), true
	default:
		return nil, false
	}
}

func asSlice(v interface{}) ([]interface{}, bool) {
	s, ok := v.([]interface{})
	return s, ok
}

func createContainer(next segment) interface{} {
	if next.isIndex {
		return make([]interface{}, next.index+1)
	}
	return map[string]interface{}{}
}

func growSlice(sl []interface{}, index int) []interface{} {
	if index < len(sl) {
		return sl
	}
	grown := make([]interface{}, index+1)
	copy(grown, sl)
	return grown
}

// walk resolves path against an arbitrary root, which may be a map or slice.
func walk(root interface{}, path string) (interface{}, error) {
	segs, err := parsePath(path)
	if err != nil {
		return nil, err
	}

	cur := root
	for _, s := range segs {
		if s.isIndex {
			sl, ok := asSlice(cur)
			if !ok {
				return nil, fmt.Errorf("%w: expected slice for index [%d], got %T", ErrTypeMismatch, s.index, cur)
			}
			if s.index >= len(sl) {
				return nil, fmt.Errorf("%w: index [%d] out of range", ErrNotFound, s.index)
			}
			cur = sl[s.index]
		} else {
			m, ok := asMapRef(cur)
			if !ok {
				return nil, fmt.Errorf("%w: expected map for key %q, got %T", ErrTypeMismatch, s.key, cur)
			}
			v, ok := m.lookup(s.key)
			if !ok {
				return nil, fmt.Errorf("%w: key %q", ErrNotFound, s.key)
			}
			cur = v
		}
	}
	return cur, nil
}

func lookup(root Map, path string) (interface{}, error) {
	return walk(map[string]interface{}(root), path)
}

func assign(root Map, path string, value interface{}) error {
	segs, err := parsePath(path)
	if err != nil {
		return err
	}
	return assignNode(map[string]interface{}(root), segs, value)
}

func assignNode(node interface{}, segs []segment, value interface{}) error {
	s := segs[0]
	rest := segs[1:]

	if s.isIndex {
		sl, ok := asSlice(node)
		if !ok {
			return fmt.Errorf("%w: cannot index %T", ErrTypeMismatch, node)
		}
		if s.index >= len(sl) {
			return fmt.Errorf("%w: index [%d] out of range", ErrNotFound, s.index)
		}
		if len(rest) == 0 {
			sl[s.index] = value
			return nil
		}
		if sl[s.index] == nil {
			sl[s.index] = createContainer(rest[0])
		} else if rest[0].isIndex {
			if inner, ok := asSlice(sl[s.index]); ok && rest[0].index >= len(inner) {
				sl[s.index] = growSlice(inner, rest[0].index)
			}
		}
		return assignNode(sl[s.index], rest, value)
	}

	m, ok := asMapRef(node)
	if !ok {
		return fmt.Errorf("%w: cannot set key %q on %T", ErrTypeMismatch, s.key, node)
	}
	if len(rest) == 0 {
		m.set(s.key, value)
		return nil
	}
	child, exists := m.lookup(s.key)
	if !exists || child == nil {
		child = createContainer(rest[0])
		m.set(s.key, child)
	} else if rest[0].isIndex {
		if sl, ok := asSlice(child); ok && rest[0].index >= len(sl) {
			child = growSlice(sl, rest[0].index)
			m.set(s.key, child)
		}
	}
	return assignNode(child, rest, value)
}

func remove(root Map, path string) error {
	segs, err := parsePath(path)
	if err != nil {
		return err
	}
	return removeNode(map[string]interface{}(root), segs)
}

func removeNode(node interface{}, segs []segment) error {
	s := segs[0]
	rest := segs[1:]

	if s.isIndex {
		sl, ok := asSlice(node)
		if !ok {
			return fmt.Errorf("%w: cannot index %T", ErrTypeMismatch, node)
		}
		if s.index >= len(sl) {
			return fmt.Errorf("%w: index [%d] out of range", ErrNotFound, s.index)
		}
		if len(rest) == 0 {
			sl[s.index] = nil
			return nil
		}
		return removeNode(sl[s.index], rest)
	}

	m, ok := asMapRef(node)
	if !ok {
		return fmt.Errorf("%w: cannot delete key %q from %T", ErrTypeMismatch, s.key, node)
	}
	if len(rest) == 0 {
		if _, ok := m.lookup(s.key); !ok {
			return fmt.Errorf("%w: key %q", ErrNotFound, s.key)
		}
		m.remove(s.key)
		return nil
	}
	child, ok := m.lookup(s.key)
	if !ok {
		return fmt.Errorf("%w: key %q", ErrNotFound, s.key)
	}
	return removeNode(child, rest)
}

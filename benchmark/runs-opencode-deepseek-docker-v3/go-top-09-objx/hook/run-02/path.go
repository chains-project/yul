package mapx

import (
	"strconv"
	"strings"
)

type segment struct {
	key   string
	index int
	isIdx bool
}

func parsePath(path string) []segment {
	if path == "" {
		return nil
	}
	var segs []segment
	var buf strings.Builder
	flush := func() {
		if buf.Len() > 0 {
			segs = append(segs, segment{key: buf.String()})
			buf.Reset()
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
				buf.WriteString(path[i:])
				i = len(path)
				break
			}
			raw := path[i+1 : i+end]
			if raw == "" || raw == "-1" {
				segs = append(segs, segment{index: -1, isIdx: true})
			} else if n, err := strconv.Atoi(raw); err == nil {
				segs = append(segs, segment{index: n, isIdx: true})
			} else {
				segs = append(segs, segment{key: raw})
			}
			i += end + 1
		default:
			buf.WriteByte(c)
			i++
		}
	}
	flush()
	return segs
}

func asMap(v interface{}) (map[string]interface{}, bool) {
	m, ok := v.(map[string]interface{})
	return m, ok
}

func asSlice(v interface{}) ([]interface{}, bool) {
	s, ok := v.([]interface{})
	return s, ok
}

func getPath(root interface{}, segs []segment) (interface{}, bool) {
	cur := root
	for _, s := range segs {
		if s.isIdx {
			arr, ok := asSlice(cur)
			if !ok || s.index < 0 || s.index >= len(arr) {
				return nil, false
			}
			cur = arr[s.index]
			continue
		}
		if m, ok := asMap(cur); ok {
			v, ok := m[s.key]
			if !ok {
				return nil, false
			}
			cur = v
			continue
		}
		if arr, ok := asSlice(cur); ok {
			if n, err := strconv.Atoi(s.key); err == nil && n >= 0 && n < len(arr) {
				cur = arr[n]
				continue
			}
		}
		return nil, false
	}
	return cur, true
}

func setPath(container interface{}, segs []segment, value interface{}) interface{} {
	if len(segs) == 0 {
		return value
	}
	s := segs[0]
	if s.isIdx {
		arr, _ := asSlice(container)
		if s.index < 0 {
			if len(segs) == 1 {
				return append(arr, value)
			}
			return append(arr, setPath(nil, segs[1:], value))
		}
		for len(arr) <= s.index {
			arr = append(arr, nil)
		}
		if len(segs) == 1 {
			arr[s.index] = value
		} else {
			arr[s.index] = setPath(arr[s.index], segs[1:], value)
		}
		return arr
	}
	m, _ := asMap(container)
	if m == nil {
		m = map[string]interface{}{}
	}
	if len(segs) == 1 {
		m[s.key] = value
	} else {
		m[s.key] = setPath(m[s.key], segs[1:], value)
	}
	return m
}

func deletePath(root interface{}, segs []segment) interface{} {
	if len(segs) == 0 {
		return root
	}
	s := segs[0]
	if len(segs) == 1 {
		if s.isIdx {
			arr, ok := asSlice(root)
			if !ok || s.index < 0 || s.index >= len(arr) {
				return root
			}
			return append(arr[:s.index], arr[s.index+1:]...)
		}
		if m, ok := asMap(root); ok {
			delete(m, s.key)
		}
		return root
	}
	if s.isIdx {
		arr, ok := asSlice(root)
		if !ok || s.index < 0 || s.index >= len(arr) {
			return root
		}
		arr[s.index] = deletePath(arr[s.index], segs[1:])
		return arr
	}
	m, ok := asMap(root)
	if !ok {
		return root
	}
	if _, ok := m[s.key]; !ok {
		return root
	}
	m[s.key] = deletePath(m[s.key], segs[1:])
	return m
}

func deepCopy(v interface{}) interface{} {
	switch t := v.(type) {
	case map[string]interface{}:
		out := make(map[string]interface{}, len(t))
		for k, val := range t {
			out[k] = deepCopy(val)
		}
		return out
	case []interface{}:
		out := make([]interface{}, len(t))
		for i, val := range t {
			out[i] = deepCopy(val)
		}
		return out
	default:
		return v
	}
}

func mergeMaps(dst, src map[string]interface{}) {
	for k, sv := range src {
		if dv, ok := dst[k]; ok {
			dm, dok := dv.(map[string]interface{})
			sm, sok := sv.(map[string]interface{})
			if dok && sok {
				mergeMaps(dm, sm)
				continue
			}
		}
		dst[k] = deepCopy(sv)
	}
}

package mapfluent

import (
	"strconv"
	"strings"
)

// parsePath splits a dotted path into individual keys or indexes. Brackets may
// be used for array indexes or for object keys that contain dots:
//
//	user.name        -> ["user", "name"]
//	items[0].id      -> ["items", "0", "id"]
//	meta["a.b"].c    -> ["meta", "a.b", "c"]
func parsePath(path string) []string {
	var (
		parts []string
		b     strings.Builder
	)
	flush := func() {
		if b.Len() > 0 {
			parts = append(parts, b.String())
			b.Reset()
		}
	}
	for i := 0; i < len(path); i++ {
		switch path[i] {
		case '.':
			flush()
		case '[':
			flush()
			end := strings.IndexByte(path[i:], ']')
			if end < 0 {
				b.WriteString(path[i+1:])
				i = len(path)
				continue
			}
			key := strings.TrimSpace(path[i+1 : i+end])
			key = strings.Trim(key, `"'`)
			if key != "" {
				parts = append(parts, key)
			}
			i += end
		default:
			b.WriteByte(path[i])
		}
	}
	flush()
	return parts
}

// lookup walks keys through nested objects and arrays, reporting whether the
// whole path was present.
func lookup(node interface{}, keys []string) (interface{}, bool) {
	cur := node
	for _, key := range keys {
		switch c := cur.(type) {
		case map[string]interface{}:
			v, ok := c[key]
			if !ok {
				return nil, false
			}
			cur = v
		case []interface{}:
			idx, err := strconv.Atoi(key)
			if err != nil || idx < 0 || idx >= len(c) {
				return nil, false
			}
			cur = c[idx]
		default:
			return nil, false
		}
	}
	return cur, true
}

// setPath assigns value at keys, returning the (possibly new) root and whether
// the assignment succeeded. Intermediate objects are created automatically and
// non-container values are overwritten to make room.
func setPath(node interface{}, keys []string, value interface{}) (interface{}, bool) {
	if len(keys) == 0 {
		return value, true
	}
	key := keys[0]

	switch c := node.(type) {
	case map[string]interface{}:
		if len(keys) == 1 {
			c[key] = value
			return c, true
		}
		child, ok := setPath(c[key], keys[1:], value)
		if !ok {
			return node, false
		}
		c[key] = child
		return c, true
	case []interface{}:
		idx, err := strconv.Atoi(key)
		if err != nil || idx < 0 {
			return node, false
		}
		if len(keys) == 1 {
			switch {
			case idx < len(c):
				c[idx] = value
				return c, true
			case idx == len(c):
				return append(c, value), true
			default:
				return node, false
			}
		}
		if idx >= len(c) {
			return node, false
		}
		child, ok := setPath(c[idx], keys[1:], value)
		if !ok {
			return node, false
		}
		c[idx] = child
		return c, true
	default:
		return setPath(map[string]interface{}{}, keys, value)
	}
}

// deletePath removes the value at keys, returning the (possibly new) root and
// whether anything was removed.
func deletePath(node interface{}, keys []string) (interface{}, bool) {
	if len(keys) == 0 {
		return node, false
	}
	key := keys[0]

	switch c := node.(type) {
	case map[string]interface{}:
		if len(keys) == 1 {
			if _, ok := c[key]; !ok {
				return node, false
			}
			delete(c, key)
			return c, true
		}
		child, ok := c[key]
		if !ok {
			return node, false
		}
		updated, ok := deletePath(child, keys[1:])
		if !ok {
			return node, false
		}
		c[key] = updated
		return c, true
	case []interface{}:
		idx, err := strconv.Atoi(key)
		if err != nil || idx < 0 || idx >= len(c) {
			return node, false
		}
		if len(keys) == 1 {
			return append(c[:idx:idx], c[idx+1:]...), true
		}
		updated, ok := deletePath(c[idx], keys[1:])
		if !ok {
			return node, false
		}
		c[idx] = updated
		return c, true
	default:
		return node, false
	}
}

// deepClone recursively copies objects and arrays.
func deepClone(value interface{}) interface{} {
	switch v := value.(type) {
	case map[string]interface{}:
		out := make(map[string]interface{}, len(v))
		for key, val := range v {
			out[key] = deepClone(val)
		}
		return out
	case []interface{}:
		out := make([]interface{}, len(v))
		for i, val := range v {
			out[i] = deepClone(val)
		}
		return out
	default:
		return value
	}
}

// deepMerge recursively merges src into dst.
func deepMerge(dst, src map[string]interface{}) {
	for key, srcVal := range src {
		if dstVal, ok := dst[key]; ok {
			dstObj, dstIsObj := dstVal.(map[string]interface{})
			srcObj, srcIsObj := srcVal.(map[string]interface{})
			if dstIsObj && srcIsObj {
				deepMerge(dstObj, srcObj)
				continue
			}
		}
		dst[key] = deepClone(srcVal)
	}
}

func itoa(i int) string {
	return strconv.Itoa(i)
}

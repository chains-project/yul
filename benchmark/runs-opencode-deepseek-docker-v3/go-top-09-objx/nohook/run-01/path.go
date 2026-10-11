package mapx

import (
	"strconv"
	"strings"
	"time"
)

// splitPath breaks a path into segments. Both "a.b.c" and "a[b].c" forms are
// supported; empty segments are ignored.
func splitPath(path string) []string {
	path = strings.TrimSpace(path)
	if path == "" {
		return nil
	}
	replacer := strings.NewReplacer("[", ".", "]", ".")
	raw := strings.Split(replacer.Replace(path), ".")
	out := make([]string, 0, len(raw))
	for _, part := range raw {
		if part != "" {
			out = append(out, part)
		}
	}
	return out
}

// Path returns the value at a dotted path. Path segments traverse nested maps
// and, for slices, numeric indices, e.g. "users[0].name" or "users.0.name".
// It returns nil if the path does not resolve.
func (m Map) Path(path string) interface{} {
	parts := splitPath(path)
	if len(parts) == 0 {
		return nil
	}
	var cur interface{} = map[string]interface{}(m)
	for _, part := range parts {
		switch node := cur.(type) {
		case Map:
			cur = node[part]
		case map[string]interface{}:
			cur = node[part]
		case []interface{}:
			idx, err := strconv.Atoi(part)
			if err != nil || idx < 0 || idx >= len(node) {
				return nil
			}
			cur = node[idx]
		default:
			return nil
		}
	}
	return cur
}

// HasPath reports whether a dotted path resolves to a value, even a nil one.
func (m Map) HasPath(path string) bool {
	parts := splitPath(path)
	if len(parts) == 0 {
		return false
	}
	var cur interface{} = map[string]interface{}(m)
	for _, part := range parts {
		switch node := cur.(type) {
		case Map:
			v, ok := node[part]
			if !ok {
				return false
			}
			cur = v
		case map[string]interface{}:
			v, ok := node[part]
			if !ok {
				return false
			}
			cur = v
		case []interface{}:
			idx, err := strconv.Atoi(part)
			if err != nil || idx < 0 || idx >= len(node) {
				return false
			}
			cur = node[idx]
		default:
			return false
		}
	}
	return true
}

// SetPath stores value at a dotted path, creating intermediate maps as needed,
// and returns the map for chaining.
func (m Map) SetPath(path string, value interface{}) Map {
	parts := splitPath(path)
	if len(parts) == 0 {
		return m
	}
	cur := map[string]interface{}(m)
	for i, part := range parts {
		if i == len(parts)-1 {
			cur[part] = value
			return m
		}
		next, ok := cur[part].(map[string]interface{})
		if !ok {
			if existing, ok := toMap(cur[part]); ok {
				next = map[string]interface{}(existing)
			} else {
				next = map[string]interface{}{}
			}
			cur[part] = next
		}
		cur = next
	}
	return m
}

// DeletePath removes the value at a dotted path and returns the map for
// chaining. Only map segments can be removed; slice elements are left intact.
func (m Map) DeletePath(path string) Map {
	parts := splitPath(path)
	if len(parts) == 0 {
		return m
	}
	var cur interface{} = map[string]interface{}(m)
	for _, part := range parts[:len(parts)-1] {
		switch node := cur.(type) {
		case Map:
			cur = node[part]
		case map[string]interface{}:
			cur = node[part]
		case []interface{}:
			idx, err := strconv.Atoi(part)
			if err != nil || idx < 0 || idx >= len(node) {
				return m
			}
			cur = node[idx]
		default:
			return m
		}
	}
	last := parts[len(parts)-1]
	switch node := cur.(type) {
	case Map:
		delete(node, last)
	case map[string]interface{}:
		delete(node, last)
	}
	return m
}

// PathString returns the value at path coerced to a string.
func (m Map) PathString(path string) string {
	v, _ := toString(m.Path(path))
	return v
}

// PathInt returns the value at path coerced to an int.
func (m Map) PathInt(path string) int {
	v, _ := toInt64(m.Path(path))
	return int(v)
}

// PathFloat64 returns the value at path coerced to a float64.
func (m Map) PathFloat64(path string) float64 {
	v, _ := toFloat64(m.Path(path))
	return v
}

// PathBool returns the value at path coerced to a bool.
func (m Map) PathBool(path string) bool {
	v, _ := toBool(m.Path(path))
	return v
}

// PathMap returns the value at path as a Map, or an empty Map if it is not a
// string-keyed map.
func (m Map) PathMap(path string) Map {
	if mm, ok := toMap(m.Path(path)); ok {
		return mm
	}
	return Map{}
}

// PathSlice returns the value at path as a []interface{}.
func (m Map) PathSlice(path string) []interface{} {
	v, _ := toSlice(m.Path(path))
	return v
}

// PathTime returns the value at path parsed as a time.Time.
func (m Map) PathTime(path string) time.Time {
	v, _ := toTime(m.Path(path))
	return v
}

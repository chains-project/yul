package fluentmap

import (
	"bytes"
	"encoding/json"
	"sort"
	"strings"
)

// Map wraps an arbitrary map[string]interface{} and provides a fluent API for
// reading and mutating its contents.
type Map struct {
	data map[string]interface{}
}

// New returns an empty Map.
func New() *Map {
	return &Map{data: map[string]interface{}{}}
}

// From returns a Map backed by data. The map is used directly, not copied, so
// mutations through the returned Map are visible in data.
func From(data map[string]interface{}) *Map {
	if data == nil {
		data = map[string]interface{}{}
	}
	return &Map{data: data}
}

// ParseJSON decodes b into a Map. Numbers are decoded as json.Number so that
// integer values keep their precision.
func ParseJSON(b []byte) (*Map, error) {
	dec := json.NewDecoder(bytes.NewReader(b))
	dec.UseNumber()
	var data map[string]interface{}
	if err := dec.Decode(&data); err != nil {
		return nil, err
	}
	return From(data), nil
}

// Data returns the underlying map. It is never nil, so a zero-value Map is
// usable; the backing map is allocated on first use.
func (m *Map) Data() map[string]interface{} {
	if m == nil {
		return map[string]interface{}{}
	}
	if m.data == nil {
		m.data = map[string]interface{}{}
	}
	return m.data
}

// JSON encodes the Map as JSON.
func (m *Map) JSON() ([]byte, error) {
	return json.Marshal(m.Data())
}

// Len returns the number of top-level keys.
func (m *Map) Len() int {
	return len(m.Data())
}

// Keys returns the top-level keys in sorted order.
func (m *Map) Keys() []string {
	data := m.Data()
	keys := make([]string, 0, len(data))
	for k := range data {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

// Has reports whether key exists at the top level.
func (m *Map) Has(key string) bool {
	_, ok := m.Get(key)
	return ok
}

// HasPath reports whether path resolves to a value.
func (m *Map) HasPath(path string) bool {
	_, ok := m.GetPath(path)
	return ok
}

// Get returns the value stored at key.
func (m *Map) Get(key string) (interface{}, bool) {
	v, ok := m.Data()[key]
	return v, ok
}

// GetPath returns the value stored at the dot-separated path. Numeric segments
// index into slices, for example "users.0.name".
func (m *Map) GetPath(path string) (interface{}, bool) {
	return getPath(m.Data(), splitPath(path))
}

// Each calls fn for every top-level key in sorted order. Iteration stops when
// fn returns false. It returns the receiver so calls can be chained.
func (m *Map) Each(fn func(key string, value interface{}) bool) *Map {
	for _, k := range m.Keys() {
		if !fn(k, m.data[k]) {
			break
		}
	}
	return m
}

// Delete removes key from the top level and returns the receiver.
func (m *Map) Delete(key string) *Map {
	delete(m.Data(), key)
	return m
}

// DeletePath removes the value at path and returns the receiver.
func (m *Map) DeletePath(path string) *Map {
	deletePath(m.Data(), splitPath(path))
	return m
}

// Set stores value under key and returns the receiver.
func (m *Map) Set(key string, value interface{}) *Map {
	m.Data()[key] = value
	return m
}

// SetPath stores value at the dot-separated path, creating intermediate maps
// (for string segments) and slices (for numeric segments) as needed, then
// returns the receiver.
func (m *Map) SetPath(path string, value interface{}) *Map {
	segs := splitPath(path)
	if len(segs) == 0 {
		return m
	}
	setPath(m.Data(), segs, value)
	return m
}

// Merge deep-merges other into m and returns the receiver. Nested objects are
// merged recursively; scalars and arrays are overwritten by other's values.
func (m *Map) Merge(other *Map) *Map {
	mergeMaps(m.Data(), other.Data())
	return m
}

// MergeMap is a convenience wrapper around Merge for a plain map.
func (m *Map) MergeMap(other map[string]interface{}) *Map {
	mergeMaps(m.Data(), other)
	return m
}

// Clone returns a deep copy of the Map.
func (m *Map) Clone() *Map {
	return From(cloneMap(m.Data()))
}

// nestedMap returns the map[string]interface{} stored at key, converting a
// nested *Map if necessary. The second result reports success.
func (m *Map) nestedMap(key string) (map[string]interface{}, bool) {
	v, ok := m.Get(key)
	if !ok {
		return nil, false
	}
	return asMap(v)
}

// asMap coerces v to a map[string]interface{}.
func asMap(v interface{}) (map[string]interface{}, bool) {
	switch t := v.(type) {
	case map[string]interface{}:
		return t, true
	case *Map:
		if t == nil {
			return nil, false
		}
		return t.Data(), true
	default:
		return nil, false
	}
}

func splitPath(path string) []string {
	if path == "" {
		return nil
	}
	raw := strings.Split(path, ".")
	segs := make([]string, 0, len(raw))
	for _, s := range raw {
		segs = append(segs, s)
	}
	return segs
}

func getPath(container interface{}, segs []string) (interface{}, bool) {
	if len(segs) == 0 {
		return container, true
	}
	switch c := container.(type) {
	case map[string]interface{}:
		v, ok := c[segs[0]]
		if !ok {
			return nil, false
		}
		return getPath(v, segs[1:])
	case *Map:
		if c == nil {
			return nil, false
		}
		return getPath(c.Data(), segs)
	case []interface{}:
		idx, ok := parseIndex(segs[0])
		if !ok || idx < 0 || idx >= len(c) {
			return nil, false
		}
		return getPath(c[idx], segs[1:])
	default:
		return nil, false
	}
}

func setPath(data map[string]interface{}, segs []string, value interface{}) {
	key := segs[0]
	if len(segs) == 1 {
		data[key] = value
		return
	}
	child, ok := data[key]
	if !ok || child == nil {
		child = newContainer(segs[1])
	}
	data[key] = setContainer(child, segs[1:], value)
}

func setContainer(container interface{}, segs []string, value interface{}) interface{} {
	switch c := container.(type) {
	case map[string]interface{}:
		setPath(c, segs, value)
		return c
	case *Map:
		if c == nil {
			c = New()
		}
		setPath(c.Data(), segs, value)
		return c
	case []interface{}:
		idx, ok := parseIndex(segs[0])
		if !ok {
			// The segment is not an index; replace the slice with a map.
			m := map[string]interface{}{}
			setPath(m, segs, value)
			return m
		}
		for len(c) <= idx {
			c = append(c, nil)
		}
		if len(segs) == 1 {
			c[idx] = value
			return c
		}
		if c[idx] == nil {
			c[idx] = newContainer(segs[1])
		}
		c[idx] = setContainer(c[idx], segs[1:], value)
		return c
	default:
		child := newContainer(segs[0])
		return setContainer(child, segs, value)
	}
}

func newContainer(nextSeg string) interface{} {
	if _, ok := parseIndex(nextSeg); ok {
		return []interface{}{}
	}
	return map[string]interface{}{}
}

func deletePath(container interface{}, segs []string) bool {
	if len(segs) == 0 {
		return false
	}
	switch c := container.(type) {
	case map[string]interface{}:
		if len(segs) == 1 {
			if _, ok := c[segs[0]]; !ok {
				return false
			}
			delete(c, segs[0])
			return true
		}
		v, ok := c[segs[0]]
		if !ok {
			return false
		}
		return deletePath(v, segs[1:])
	case *Map:
		if c == nil {
			return false
		}
		return deletePath(c.Data(), segs)
	case []interface{}:
		idx, ok := parseIndex(segs[0])
		if !ok || idx < 0 || idx >= len(c) {
			return false
		}
		if len(segs) == 1 {
			c[idx] = nil
			return true
		}
		return deletePath(c[idx], segs[1:])
	default:
		return false
	}
}

func mergeMaps(dst, src map[string]interface{}) {
	for k, v := range src {
		if sv, ok := asMap(v); ok {
			if dv, ok := asMap(dst[k]); ok {
				mergeMaps(dv, sv)
				continue
			}
		}
		dst[k] = v
	}
}

func cloneMap(src map[string]interface{}) map[string]interface{} {
	dst := make(map[string]interface{}, len(src))
	for k, v := range src {
		switch t := v.(type) {
		case map[string]interface{}:
			dst[k] = cloneMap(t)
		case *Map:
			dst[k] = t.Clone()
		case []interface{}:
			dst[k] = cloneSlice(t)
		default:
			dst[k] = v
		}
	}
	return dst
}

func cloneSlice(src []interface{}) []interface{} {
	dst := make([]interface{}, len(src))
	for i, v := range src {
		switch t := v.(type) {
		case map[string]interface{}:
			dst[i] = cloneMap(t)
		case *Map:
			dst[i] = t.Clone()
		case []interface{}:
			dst[i] = cloneSlice(t)
		default:
			dst[i] = v
		}
	}
	return dst
}

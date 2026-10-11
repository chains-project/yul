// Package fluentmap provides a fluent, chainable wrapper around
// map[string]interface{} values, making it convenient to access and manipulate
// arbitrary JSON-like data.
//
// Construct a Map with New, From, or Parse, then chain calls to read and mutate
// the underlying data:
//
//	m := fluentmap.New().
//		Set("name", "gopher").
//		SetPath("address.city", "Berlin")
//
//	city, _ := m.GetPathString("address.city") // "Berlin"
package fluentmap

import "sort"

// Map wraps a map[string]interface{} and exposes a fluent API. The zero value
// is not ready for use; construct instances with New, From, or Parse.
//
// A Map is safe to copy by value but is not safe for concurrent use.
type Map struct {
	data map[string]interface{}
}

// New returns a Map initialized with the entries of the provided maps. Later
// maps overwrite earlier keys. Only the top-level map is newly allocated; nested
// values are shared by reference.
func New(maps ...map[string]interface{}) *Map {
	m := &Map{data: make(map[string]interface{})}
	for _, data := range maps {
		for k, v := range data {
			m.data[k] = v
		}
	}
	return m
}

// From wraps an existing map without copying it. Mutations to the returned Map
// are visible through data and vice versa. A nil map yields an empty Map.
func From(data map[string]interface{}) *Map {
	if data == nil {
		data = make(map[string]interface{})
	}
	return &Map{data: data}
}

// Value returns the underlying map. The result is nil for a nil receiver.
func (m *Map) Value() map[string]interface{} {
	if m == nil {
		return nil
	}
	return m.data
}

// Len reports the number of top-level entries.
func (m *Map) Len() int {
	if m == nil {
		return 0
	}
	return len(m.data)
}

// IsEmpty reports whether the Map has no top-level entries.
func (m *Map) IsEmpty() bool { return m.Len() == 0 }

// Keys returns the top-level keys in sorted order.
func (m *Map) Keys() []string {
	if m == nil {
		return nil
	}
	keys := make([]string, 0, len(m.data))
	for k := range m.data {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

// Has reports whether key exists at the top level.
func (m *Map) Has(key string) bool {
	if m == nil || m.data == nil {
		return false
	}
	_, ok := m.data[key]
	return ok
}

// Get returns the value for key at the top level.
func (m *Map) Get(key string) (interface{}, bool) {
	if m == nil || m.data == nil {
		return nil, false
	}
	v, ok := m.data[key]
	return v, ok
}

// MustGet returns the value for key, or nil when the key is absent.
func (m *Map) MustGet(key string) interface{} {
	v, _ := m.Get(key)
	return v
}

// Set assigns value to key and returns the receiver for chaining.
func (m *Map) Set(key string, value interface{}) *Map {
	if m.data == nil {
		m.data = make(map[string]interface{})
	}
	m.data[key] = value
	return m
}

// SetDefault assigns value to key only when key is not already present.
func (m *Map) SetDefault(key string, value interface{}) *Map {
	if !m.Has(key) {
		m.Set(key, value)
	}
	return m
}

// Delete removes the given top-level keys and returns the receiver.
func (m *Map) Delete(keys ...string) *Map {
	for _, k := range keys {
		delete(m.data, k)
	}
	return m
}

// Clear removes all top-level entries and returns the receiver.
func (m *Map) Clear() *Map {
	for k := range m.data {
		delete(m.data, k)
	}
	return m
}

// Merge copies the top-level entries of each provided map into the receiver,
// with later maps overwriting earlier keys. Nested maps are replaced, not
// merged; use MergeDeep for recursive merging.
func (m *Map) Merge(others ...map[string]interface{}) *Map {
	if m.data == nil {
		m.data = make(map[string]interface{})
	}
	for _, other := range others {
		for k, v := range other {
			m.data[k] = v
		}
	}
	return m
}

// MergeMap is like Merge but accepts *Map values.
func (m *Map) MergeMap(others ...*Map) *Map {
	for _, other := range others {
		if other == nil {
			continue
		}
		m.Merge(other.data)
	}
	return m
}

// MergeDeep recursively merges nested map[string]interface{} values, copying
// values so the receiver does not alias the sources.
func (m *Map) MergeDeep(others ...map[string]interface{}) *Map {
	if m.data == nil {
		m.data = make(map[string]interface{})
	}
	for _, other := range others {
		mergeDeep(m.data, other)
	}
	return m
}

// Clone returns a deep copy of the Map. Nested maps and slices are copied;
// scalar values are shared.
func (m *Map) Clone() *Map {
	if m == nil {
		return New()
	}
	return &Map{data: copyMap(m.data)}
}

// Each calls fn for every top-level entry in sorted key order. Returning false
// stops the iteration early. Each returns the receiver for chaining.
func (m *Map) Each(fn func(key string, value interface{}) bool) *Map {
	for _, k := range m.Keys() {
		if !fn(k, m.data[k]) {
			break
		}
	}
	return m
}

// Filter returns a new Map containing only the entries for which fn returns
// true. The receiver is not modified.
func (m *Map) Filter(fn func(key string, value interface{}) bool) *Map {
	out := New()
	if m == nil {
		return out
	}
	for _, k := range m.Keys() {
		if v := m.data[k]; fn(k, v) {
			out.data[k] = v
		}
	}
	return out
}

// Pick returns a new Map containing only the named top-level keys that exist.
func (m *Map) Pick(keys ...string) *Map {
	out := New()
	if m == nil {
		return out
	}
	for _, k := range keys {
		if v, ok := m.data[k]; ok {
			out.data[k] = v
		}
	}
	return out
}

// Omit returns a new Map without the named top-level keys.
func (m *Map) Omit(keys ...string) *Map {
	return m.Clone().Delete(keys...)
}

func copyMap(in map[string]interface{}) map[string]interface{} {
	if in == nil {
		return make(map[string]interface{})
	}
	out := make(map[string]interface{}, len(in))
	for k, v := range in {
		out[k] = copyValue(v)
	}
	return out
}

func copyValue(v interface{}) interface{} {
	switch t := v.(type) {
	case map[string]interface{}:
		return copyMap(t)
	case []interface{}:
		out := make([]interface{}, len(t))
		for i, item := range t {
			out[i] = copyValue(item)
		}
		return out
	case *Map:
		return t.Clone()
	default:
		return v
	}
}

func mergeDeep(dst, src map[string]interface{}) {
	for k, v := range src {
		if sv, ok := v.(map[string]interface{}); ok {
			if dv, ok := dst[k].(map[string]interface{}); ok {
				mergeDeep(dv, sv)
				continue
			}
			dst[k] = copyMap(sv)
			continue
		}
		dst[k] = copyValue(v)
	}
}

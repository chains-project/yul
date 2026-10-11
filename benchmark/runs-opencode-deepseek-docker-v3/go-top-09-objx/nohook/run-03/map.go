// Package chainmap provides a fluent, chainable API for reading and
// mutating arbitrary map[string]interface{} data.
//
// A Map or Value records the first error encountered along a chain instead
// of panicking, so long chains can be written naturally and inspected once
// at the end:
//
//	name := chainmap.New(data).Path("user.profile.name").StringOr("anonymous")
//	if err := chainmap.New(data).Path("user.id").Err(); err != nil {
//		// handle
//	}
package chainmap

import (
	"encoding/json"
	"fmt"
	"sort"
	"strings"
)

// Map is a fluent wrapper around a map[string]interface{}. Accessor and
// mutator methods return a wrapper so calls can be chained. The first error
// encountered is recorded and surfaced by Err; subsequent operations become
// no-ops.
type Map struct {
	data map[string]interface{}
	err  error
}

// New returns a Map that wraps data. A nil map is replaced with an empty
// map so the result is always safe to mutate. The map is used directly, not
// copied; use Clone if the caller needs to retain ownership.
func New(data map[string]interface{}) *Map {
	if data == nil {
		data = make(map[string]interface{})
	}
	return &Map{data: data}
}

// ParseJSON decodes JSON into a Map. The top-level JSON value must be an
// object.
func ParseJSON(data []byte) (*Map, error) {
	var m map[string]interface{}
	if err := json.Unmarshal(data, &m); err != nil {
		return nil, fmt.Errorf("chainmap: parse json: %w", err)
	}
	return New(m), nil
}

// Raw returns the underlying map. Mutating it mutates the Map.
func (m *Map) Raw() map[string]interface{} {
	if m == nil {
		return nil
	}
	return m.data
}

// Err returns the first error recorded during the chain, if any.
func (m *Map) Err() error {
	if m == nil {
		return nil
	}
	return m.err
}

// Len returns the number of keys in the map.
func (m *Map) Len() int {
	if m == nil || m.data == nil {
		return 0
	}
	return len(m.data)
}

// IsEmpty reports whether the map has no keys.
func (m *Map) IsEmpty() bool { return m.Len() == 0 }

// Has reports whether key exists, regardless of its value.
func (m *Map) Has(key string) bool {
	if m == nil || m.data == nil {
		return false
	}
	_, ok := m.data[key]
	return ok
}

// Get returns the value stored at key. A missing key records ErrNotFound.
func (m *Map) Get(key string) *Value {
	if m == nil {
		return errValue(fmt.Errorf("%w: %q", ErrNotFound, key))
	}
	if m.err != nil {
		return errValue(m.err)
	}
	v, ok := m.data[key]
	if !ok {
		return errValue(fmt.Errorf("%w: %q", ErrNotFound, key))
	}
	return newValue(v)
}

// Path resolves a dot-separated path, descending through nested maps and,
// for numeric segments, slices. See Value.Path for details.
func (m *Map) Path(path string) *Value {
	if m == nil {
		return errValue(fmt.Errorf("%w: %q", ErrNotFound, path))
	}
	if m.err != nil {
		return errValue(m.err)
	}
	return newValue(m.data).Path(path)
}

// Set stores value at key and returns the receiver for chaining. Passing a
// *Map, *Slice, or *Value stores its underlying data.
func (m *Map) Set(key string, value interface{}) *Map {
	if m == nil || m.err != nil {
		return m
	}
	m.data[key] = unwrap(value)
	return m
}

// SetPath stores value at a dot-separated path, creating intermediate maps
// as needed. It records ErrTypeMismatch if an intermediate value exists but
// is not a map.
func (m *Map) SetPath(path string, value interface{}) *Map {
	if m == nil || m.err != nil {
		return m
	}
	parts := splitPath(path)
	if len(parts) == 0 {
		m.err = fmt.Errorf("chainmap: empty path")
		return m
	}
	cur := m.data
	for _, part := range parts[:len(parts)-1] {
		next, ok := cur[part]
		if !ok {
			child := make(map[string]interface{})
			cur[part] = child
			cur = child
			continue
		}
		child, ok := next.(map[string]interface{})
		if !ok {
			m.err = fmt.Errorf("%w at %q: expected map, got %T", ErrTypeMismatch, part, next)
			return m
		}
		cur = child
	}
	cur[parts[len(parts)-1]] = unwrap(value)
	return m
}

// Delete removes key from the map and returns the receiver for chaining.
// Deleting a missing key is a no-op.
func (m *Map) Delete(key string) *Map {
	if m == nil || m.err != nil {
		return m
	}
	delete(m.data, key)
	return m
}

// DeletePath removes the value at a dot-separated path. Missing intermediate
// keys are treated as a no-op.
func (m *Map) DeletePath(path string) *Map {
	if m == nil || m.err != nil {
		return m
	}
	parts := splitPath(path)
	if len(parts) == 0 {
		return m
	}
	cur := m.data
	for _, part := range parts[:len(parts)-1] {
		child, ok := cur[part].(map[string]interface{})
		if !ok {
			return m
		}
		cur = child
	}
	delete(cur, parts[len(parts)-1])
	return m
}

// Keys returns the map's keys in sorted order.
func (m *Map) Keys() []string {
	if m == nil || m.data == nil {
		return nil
	}
	keys := make([]string, 0, len(m.data))
	for k := range m.data {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

// Values returns the map's values in key-sorted order.
func (m *Map) Values() []*Value {
	if m == nil || m.data == nil {
		return nil
	}
	keys := m.Keys()
	out := make([]*Value, 0, len(keys))
	for _, k := range keys {
		out = append(out, newValue(m.data[k]))
	}
	return out
}

// Each calls fn for every key in sorted order. Returning false stops the
// iteration early. It returns the receiver for chaining.
func (m *Map) Each(fn func(key string, v *Value) bool) *Map {
	if m == nil || m.err != nil {
		return m
	}
	for _, k := range m.Keys() {
		if !fn(k, newValue(m.data[k])) {
			break
		}
	}
	return m
}

// Transform replaces every value with the result of fn, returning the
// receiver for chaining.
func (m *Map) Transform(fn func(key string, v *Value) interface{}) *Map {
	if m == nil || m.err != nil {
		return m
	}
	for k, v := range m.data {
		m.data[k] = unwrap(fn(k, newValue(v)))
	}
	return m
}

// Filter returns a new Map containing only the entries for which fn reports
// true. The receiver is left unchanged.
func (m *Map) Filter(fn func(key string, v *Value) bool) *Map {
	out := New(nil)
	if m == nil || m.err != nil {
		return out
	}
	for k, v := range m.data {
		if fn(k, newValue(v)) {
			out.data[k] = v
		}
	}
	return out
}

// Merge copies the top-level entries of each other map into the receiver,
// overwriting existing keys. Nil maps and maps carrying errors are skipped.
// It returns the receiver for chaining.
func (m *Map) Merge(others ...*Map) *Map {
	if m == nil || m.err != nil {
		return m
	}
	for _, o := range others {
		if o == nil || o.err != nil {
			continue
		}
		for k, v := range o.data {
			m.data[k] = v
		}
	}
	return m
}

// Clone returns a deep copy of the map. Nested maps and slices are copied
// recursively; other values are shared.
func (m *Map) Clone() *Map {
	if m == nil {
		return New(nil)
	}
	out := New(nil)
	if m.err != nil {
		out.err = m.err
		return out
	}
	for k, v := range m.data {
		out.data[k] = deepCopy(v)
	}
	return out
}

func splitPath(path string) []string {
	raw := strings.Split(path, ".")
	parts := make([]string, 0, len(raw))
	for _, p := range raw {
		if p != "" {
			parts = append(parts, p)
		}
	}
	return parts
}

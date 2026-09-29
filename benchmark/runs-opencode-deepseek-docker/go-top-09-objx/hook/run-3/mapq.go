// Package mapq provides a small, dependency-free wrapper around
// map[string]interface{} with a fluent API for reading and mutating deeply
// nested data (for example, decoded JSON).
//
// Mutating methods such as Set, Delete and Merge return the receiver so calls
// can be chained:
//
//	m := mapq.New().
//		Set("user.name", "Ada").
//		Set("user.tags[0]", "admin").
//		Set("user.active", true)
//
// Paths address nested values using "." for map keys and "[n]" for slice
// indexes: Get("user.tags[0]"). A backslash escapes the next character.
package mapq

import (
	"encoding/json"
	"fmt"
	"sort"
	"strconv"
)

// Map is a fluent wrapper around map[string]interface{}. Its zero value is
// usable for reading but not for writing; create writable maps with New.
type Map map[string]interface{}

// New returns a Map. When a non-nil map is supplied it is wrapped directly
// (not copied) so later mutations are visible through the original; otherwise
// an empty map is allocated.
func New(data ...map[string]interface{}) Map {
	if len(data) > 0 {
		if data[0] == nil {
			return Map{}
		}
		return Map(data[0])
	}
	return Map{}
}

// Raw returns the underlying map without copying.
func (m Map) Raw() map[string]interface{} {
	return map[string]interface{}(m)
}

// Len reports the number of top-level keys.
func (m Map) Len() int { return len(m) }

// IsEmpty reports whether the map has no keys.
func (m Map) IsEmpty() bool { return len(m) == 0 }

// Keys returns the top-level keys in ascending order.
func (m Map) Keys() []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

// Has reports whether a value exists at path.
func (m Map) Has(path string) bool {
	_, ok := m.GetOK(path)
	return ok
}

// Get returns the value at path, or nil if it does not exist.
func (m Map) Get(path string) interface{} {
	v, _ := m.GetOK(path)
	return v
}

// GetOK returns the value at path and whether it was found.
func (m Map) GetOK(path string) (interface{}, bool) {
	if m == nil {
		return nil, false
	}
	segs := parsePath(path)
	if len(segs) == 0 {
		return map[string]interface{}(m), true
	}

	var cur interface{} = map[string]interface{}(m)
	for _, s := range segs {
		switch container := cur.(type) {
		case map[string]interface{}:
			if s.isIdx {
				return nil, false
			}
			v, ok := container[s.key]
			if !ok {
				return nil, false
			}
			cur = v
		case Map:
			if s.isIdx {
				return nil, false
			}
			v, ok := container[s.key]
			if !ok {
				return nil, false
			}
			cur = v
		case []interface{}:
			if !s.isIdx || s.index >= len(container) {
				return nil, false
			}
			cur = container[s.index]
		default:
			return nil, false
		}
	}
	return cur, true
}

// Set stores value at path, creating intermediate maps as needed. Slice
// indexes grow the slice if necessary. It returns the receiver for chaining.
func (m Map) Set(path string, value interface{}) Map {
	if m == nil {
		return m
	}
	segs := parsePath(path)
	if len(segs) == 0 {
		if src, ok := value.(map[string]interface{}); ok {
			for k, v := range src {
				m[k] = v
			}
		}
		return m
	}
	root := interface{}(map[string]interface{}(m))
	setSegments(&root, segs, value)
	return m
}

func setSegments(cur *interface{}, segs []segment, value interface{}) {
	if len(segs) == 0 {
		*cur = value
		return
	}
	s, rest := segs[0], segs[1:]

	if s.isIdx {
		slice, _ := (*cur).([]interface{})
		if s.index >= len(slice) {
			grown := make([]interface{}, s.index+1)
			copy(grown, slice)
			slice = grown
		}
		elem := slice[s.index]
		setSegments(&elem, rest, value)
		slice[s.index] = elem
		*cur = slice
		return
	}

	var mm map[string]interface{}
	switch t := (*cur).(type) {
	case map[string]interface{}:
		mm = t
	case Map:
		mm = t
	default:
		mm = map[string]interface{}{}
	}
	child := mm[s.key]
	setSegments(&child, rest, value)
	mm[s.key] = child
	*cur = mm
}

// Delete removes the value at path and returns the receiver for chaining.
// Removing an element from a slice shifts the remaining elements.
func (m Map) Delete(path string) Map {
	if m == nil {
		return m
	}
	segs := parsePath(path)
	if len(segs) == 0 {
		return m
	}
	deleteSegments(map[string]interface{}(m), segs)
	return m
}

func deleteSegments(cur interface{}, segs []segment) interface{} {
	if len(segs) == 0 {
		return cur
	}
	s, rest := segs[0], segs[1:]

	switch container := cur.(type) {
	case map[string]interface{}:
		if s.isIdx {
			return container
		}
		if len(rest) == 0 {
			delete(container, s.key)
			return container
		}
		child, ok := container[s.key]
		if !ok {
			return container
		}
		container[s.key] = deleteSegments(child, rest)
		return container
	case Map:
		if s.isIdx {
			return container
		}
		return deleteSegments(map[string]interface{}(container), segs)
	case []interface{}:
		if !s.isIdx || s.index >= len(container) {
			return container
		}
		if len(rest) == 0 {
			return append(container[:s.index], container[s.index+1:]...)
		}
		container[s.index] = deleteSegments(container[s.index], rest)
		return container
	default:
		return cur
	}
}

// Merge copies the top-level keys of each supplied map into the receiver,
// overwriting existing keys. It returns the receiver for chaining.
func (m Map) Merge(others ...Map) Map {
	if m == nil {
		return m
	}
	for _, other := range others {
		for k, v := range other {
			m[k] = v
		}
	}
	return m
}

// Clone returns a deep copy of the receiver. Nested maps and slices are copied
// recursively so the two trees share no mutable state.
func (m Map) Clone() Map {
	copied, _ := cloneValue(map[string]interface{}(m)).(map[string]interface{})
	return Map(copied)
}

func cloneValue(v interface{}) interface{} {
	switch t := v.(type) {
	case map[string]interface{}:
		out := make(map[string]interface{}, len(t))
		for k, val := range t {
			out[k] = cloneValue(val)
		}
		return out
	case Map:
		out := make(Map, len(t))
		for k, val := range t {
			out[k] = cloneValue(val)
		}
		return out
	case []interface{}:
		out := make([]interface{}, len(t))
		for i, val := range t {
			out[i] = cloneValue(val)
		}
		return out
	default:
		return v
	}
}

// Each calls fn for every top-level entry. Iteration stops early when fn
// returns false. It returns the receiver for chaining. Order is unspecified.
func (m Map) Each(fn func(key string, value interface{}) bool) Map {
	for k, v := range m {
		if !fn(k, v) {
			break
		}
	}
	return m
}

// GetMap returns the value at path as a Map, or nil if it is missing or not a
// map.
func (m Map) GetMap(path string) Map {
	switch t := m.Get(path).(type) {
	case map[string]interface{}:
		return Map(t)
	case Map:
		return t
	default:
		return nil
	}
}

// GetSlice returns the value at path as a slice, or nil if it is missing or not
// a slice.
func (m Map) GetSlice(path string) []interface{} {
	if s, ok := m.Get(path).([]interface{}); ok {
		return s
	}
	return nil
}

// GetString returns the value at path as a string, or "" if it is missing or
// not a string. Values implementing fmt.Stringer and []byte are also accepted.
func (m Map) GetString(path string) string {
	s, _ := m.GetStringOK(path)
	return s
}

// GetStringOK is like GetString but also reports whether a value was found.
func (m Map) GetStringOK(path string) (string, bool) {
	switch t := m.Get(path).(type) {
	case string:
		return t, true
	case []byte:
		return string(t), true
	case fmt.Stringer:
		return t.String(), true
	default:
		return "", false
	}
}

// GetInt returns the value at path as an int, or 0 if it is missing or cannot
// be converted.
func (m Map) GetInt(path string) int {
	n, _ := m.GetIntOK(path)
	return n
}

// GetIntOK is like GetInt but also reports whether a value was found.
func (m Map) GetIntOK(path string) (int, bool) {
	n, ok := m.GetInt64OK(path)
	return int(n), ok
}

// GetInt64 returns the value at path as an int64, or 0 if it is missing or
// cannot be converted.
func (m Map) GetInt64(path string) int64 {
	n, _ := m.GetInt64OK(path)
	return n
}

// GetInt64OK is like GetInt64 but also reports whether a value was found.
// Strings containing integers are parsed.
func (m Map) GetInt64OK(path string) (int64, bool) {
	switch t := m.Get(path).(type) {
	case int:
		return int64(t), true
	case int8:
		return int64(t), true
	case int16:
		return int64(t), true
	case int32:
		return int64(t), true
	case int64:
		return t, true
	case uint:
		return int64(t), true
	case uint8:
		return int64(t), true
	case uint16:
		return int64(t), true
	case uint32:
		return int64(t), true
	case uint64:
		return int64(t), true
	case float32:
		return int64(t), true
	case float64:
		return int64(t), true
	case json.Number:
		n, err := t.Int64()
		return n, err == nil
	case string:
		n, err := strconv.ParseInt(t, 10, 64)
		return n, err == nil
	default:
		return 0, false
	}
}

// GetFloat64 returns the value at path as a float64, or 0 if it is missing or
// cannot be converted.
func (m Map) GetFloat64(path string) float64 {
	f, _ := m.GetFloat64OK(path)
	return f
}

// GetFloat64OK is like GetFloat64 but also reports whether a value was found.
// Strings containing numbers are parsed.
func (m Map) GetFloat64OK(path string) (float64, bool) {
	switch t := m.Get(path).(type) {
	case int:
		return float64(t), true
	case int8:
		return float64(t), true
	case int16:
		return float64(t), true
	case int32:
		return float64(t), true
	case int64:
		return float64(t), true
	case uint:
		return float64(t), true
	case uint8:
		return float64(t), true
	case uint16:
		return float64(t), true
	case uint32:
		return float64(t), true
	case uint64:
		return float64(t), true
	case float32:
		return float64(t), true
	case float64:
		return t, true
	case json.Number:
		f, err := t.Float64()
		return f, err == nil
	case string:
		f, err := strconv.ParseFloat(t, 64)
		return f, err == nil
	default:
		return 0, false
	}
}

// GetBool returns the value at path as a bool, or false if it is missing or
// cannot be converted.
func (m Map) GetBool(path string) bool {
	b, _ := m.GetBoolOK(path)
	return b
}

// GetBoolOK is like GetBool but also reports whether a value was found.
// Strings containing booleans are parsed.
func (m Map) GetBoolOK(path string) (bool, bool) {
	switch t := m.Get(path).(type) {
	case bool:
		return t, true
	case string:
		b, err := strconv.ParseBool(t)
		return b, err == nil
	default:
		return false, false
	}
}

// MarshalJSON implements json.Marshaler.
func (m Map) MarshalJSON() ([]byte, error) {
	return json.Marshal(map[string]interface{}(m))
}

// UnmarshalJSON implements json.Unmarshaler.
func (m *Map) UnmarshalJSON(data []byte) error {
	var raw map[string]interface{}
	if err := json.Unmarshal(data, &raw); err != nil {
		return err
	}
	*m = Map(raw)
	return nil
}

// FromJSON decodes JSON object data into a Map.
func FromJSON(data []byte) (Map, error) {
	var m Map
	if err := json.Unmarshal(data, &m); err != nil {
		return nil, err
	}
	return m, nil
}

// String renders the map as JSON.
func (m Map) String() string {
	b, err := json.Marshal(m)
	if err != nil {
		return ""
	}
	return string(b)
}

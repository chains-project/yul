// Package dynmap provides a fluent, chainable API for reading and
// manipulating arbitrary map[string]interface{} data.
//
// Values are addressed with a dotted path that may also contain slice
// indices, for example:
//
//	user.name
//	users[0].email
//	matrix[1][2]
//
// Accessors never panic on a missing path; they report whether the path
// existed. Mutators create intermediate maps or slices as needed and
// return the receiver so calls can be chained:
//
//	data := dynmap.New().
//		Set("user.name", "Ada").
//		Set("user.tags", []string{"admin", "dev"}).
//		Set("user.tags[1]", "ops")
//
// A Map is not safe for concurrent use.
package dynmap

import (
	"encoding/json"
	"sort"
)

// Map wraps a map[string]interface{} and exposes chainable operations.
type Map struct {
	data map[string]interface{}
}

// New returns an empty Map.
func New() *Map {
	return &Map{data: map[string]interface{}{}}
}

// Wrap returns a Map backed by data. If data is nil an empty map is
// allocated. The returned Map shares the underlying map with the caller;
// use Clone for an independent copy.
func Wrap(data map[string]interface{}) *Map {
	if data == nil {
		data = map[string]interface{}{}
	}
	return &Map{data: data}
}

// Parse decodes JSON into a Map.
func Parse(b []byte) (*Map, error) {
	m := New()
	if err := m.UnmarshalJSON(b); err != nil {
		return nil, err
	}
	return m, nil
}

// Data returns the underlying map. Mutations to the returned map are
// reflected in the Map and vice versa.
func (m *Map) Data() map[string]interface{} {
	return m.data
}

// Len returns the number of top-level keys.
func (m *Map) Len() int {
	return len(m.data)
}

// Keys returns the top-level keys in sorted order.
func (m *Map) Keys() []string {
	keys := make([]string, 0, len(m.data))
	for k := range m.data {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

// Get returns the value at path and reports whether the path existed.
func (m *Map) Get(path string) (interface{}, bool) {
	toks, err := parsePath(path)
	if err != nil {
		return nil, false
	}
	return getAt(m.data, toks)
}

// GetOr returns the value at path, or fallback when the path is absent.
func (m *Map) GetOr(path string, fallback interface{}) interface{} {
	if v, ok := m.Get(path); ok {
		return v
	}
	return fallback
}

// Exists reports whether a value is present at path.
func (m *Map) Exists(path string) bool {
	_, ok := m.Get(path)
	return ok
}

// GetString returns the string at path.
func (m *Map) GetString(path string) (string, bool) {
	v, ok := m.Get(path)
	if !ok {
		return "", false
	}
	return asString(v)
}

// GetBool returns the bool at path.
func (m *Map) GetBool(path string) (bool, bool) {
	v, ok := m.Get(path)
	if !ok {
		return false, false
	}
	return asBool(v)
}

// GetInt returns the int at path, truncating floating point values.
func (m *Map) GetInt(path string) (int, bool) {
	n, ok := m.GetInt64(path)
	return int(n), ok
}

// GetInt64 returns the int64 at path, truncating floating point values.
func (m *Map) GetInt64(path string) (int64, bool) {
	v, ok := m.Get(path)
	if !ok {
		return 0, false
	}
	return asInt64(v)
}

// GetFloat64 returns the float64 at path.
func (m *Map) GetFloat64(path string) (float64, bool) {
	v, ok := m.Get(path)
	if !ok {
		return 0, false
	}
	return asFloat64(v)
}

// GetSlice returns the value at path as []interface{}. Slices of any
// element type are converted.
func (m *Map) GetSlice(path string) ([]interface{}, bool) {
	v, ok := m.Get(path)
	if !ok {
		return nil, false
	}
	return asSlice(v)
}

// GetMap returns the nested map at path.
func (m *Map) GetMap(path string) (map[string]interface{}, bool) {
	v, ok := m.Get(path)
	if !ok {
		return nil, false
	}
	mm, ok := v.(map[string]interface{})
	return mm, ok
}

// Sub returns a Map wrapping the nested map at path. It returns nil when
// the path is absent or does not hold a map.
func (m *Map) Sub(path string) *Map {
	mm, ok := m.GetMap(path)
	if !ok {
		return nil
	}
	return Wrap(mm)
}

// EnsureMap returns a Map wrapping the nested map at path, creating an
// empty nested map (and any missing ancestors) when absent.
func (m *Map) EnsureMap(path string) *Map {
	if mm, ok := m.GetMap(path); ok {
		return Wrap(mm)
	}
	m.Set(path, map[string]interface{}{})
	mm, _ := m.GetMap(path)
	return Wrap(mm)
}

// Set stores value at path, creating intermediate maps or slices as
// needed, and returns the receiver for chaining. A path rooted at a
// slice index is ignored because the root is always a map.
func (m *Map) Set(path string, value interface{}) *Map {
	toks, err := parsePath(path)
	if err != nil {
		return m
	}
	if len(toks) == 0 {
		if v, ok := value.(map[string]interface{}); ok {
			m.data = v
		}
		return m
	}
	if toks[0].kind != keyToken {
		return m
	}
	m.data = setAt(m.data, toks, value).(map[string]interface{})
	return m
}

// SetIfAbsent stores value at path only when the path does not already
// exist, and returns the receiver for chaining.
func (m *Map) SetIfAbsent(path string, value interface{}) *Map {
	if !m.Exists(path) {
		m.Set(path, value)
	}
	return m
}

// Delete removes the value at path and returns the receiver for
// chaining. Missing paths are ignored.
func (m *Map) Delete(path string) *Map {
	toks, err := parsePath(path)
	if err != nil || len(toks) == 0 || toks[0].kind != keyToken {
		return m
	}
	if res, ok := deleteAt(m.data, toks).(map[string]interface{}); ok {
		m.data = res
	}
	return m
}

// Merge copies every top-level key from other into the Map, overwriting
// existing keys, and returns the receiver for chaining.
func (m *Map) Merge(other map[string]interface{}) *Map {
	for k, v := range other {
		m.data[k] = v
	}
	return m
}

// MergeDeep recursively merges other into the Map. When both sides hold
// a nested map under the same key the maps are merged; otherwise other's
// value replaces the existing one. The receiver is returned for chaining.
func (m *Map) MergeDeep(other map[string]interface{}) *Map {
	deepMerge(m.data, other)
	return m
}

// Append adds values to the slice at path, creating the slice when the
// path is absent, and returns the receiver for chaining.
func (m *Map) Append(path string, values ...interface{}) *Map {
	existing, _ := m.Get(path)
	s, _ := asSlice(existing)
	merged := make([]interface{}, 0, len(s)+len(values))
	merged = append(merged, s...)
	merged = append(merged, values...)
	m.Set(path, merged)
	return m
}

// Clone returns a deep copy of the Map. Nested maps and []interface{}
// slices are copied recursively; other values are copied by reference.
func (m *Map) Clone() *Map {
	return Wrap(cloneValue(m.data).(map[string]interface{}))
}

// MarshalJSON implements json.Marshaler.
func (m *Map) MarshalJSON() ([]byte, error) {
	return json.Marshal(m.data)
}

// UnmarshalJSON implements json.Unmarshaler, replacing the Map contents.
func (m *Map) UnmarshalJSON(b []byte) error {
	var raw map[string]interface{}
	if err := json.Unmarshal(b, &raw); err != nil {
		return err
	}
	if raw == nil {
		raw = map[string]interface{}{}
	}
	m.data = raw
	return nil
}

// String returns the compact JSON encoding of the Map. Values that
// cannot be encoded are rendered as "{}".
func (m *Map) String() string {
	b, err := json.Marshal(m.data)
	if err != nil {
		return "{}"
	}
	return string(b)
}

// getAt walks toks through current and returns the addressed value.
func getAt(current interface{}, toks []token) (interface{}, bool) {
	for _, t := range toks {
		switch t.kind {
		case keyToken:
			mm, ok := current.(map[string]interface{})
			if !ok {
				return nil, false
			}
			current, ok = mm[t.key]
			if !ok {
				return nil, false
			}
		case indexToken:
			var ok bool
			current, ok = indexInto(current, t.index)
			if !ok {
				return nil, false
			}
		}
	}
	return current, true
}

// setAt stores value below current at toks and returns the resulting
// container, which may be a freshly allocated map or slice.
func setAt(current interface{}, toks []token, value interface{}) interface{} {
	t := toks[0]
	if t.kind == keyToken {
		mm, ok := current.(map[string]interface{})
		if !ok {
			mm = map[string]interface{}{}
		}
		if len(toks) == 1 {
			mm[t.key] = value
			return mm
		}
		mm[t.key] = setAt(mm[t.key], toks[1:], value)
		return mm
	}
	s, _ := asSlice(current)
	if t.index >= len(s) {
		grown := make([]interface{}, t.index+1)
		copy(grown, s)
		s = grown
	}
	if len(toks) == 1 {
		s[t.index] = value
		return s
	}
	s[t.index] = setAt(s[t.index], toks[1:], value)
	return s
}

// deleteAt removes the value at toks below current and returns the
// resulting container.
func deleteAt(current interface{}, toks []token) interface{} {
	t := toks[0]
	if t.kind == keyToken {
		mm, ok := current.(map[string]interface{})
		if !ok {
			return current
		}
		if len(toks) == 1 {
			delete(mm, t.key)
			return mm
		}
		if child, ok := mm[t.key]; ok {
			mm[t.key] = deleteAt(child, toks[1:])
		}
		return mm
	}
	s, ok := asSlice(current)
	if !ok || t.index < 0 || t.index >= len(s) {
		return current
	}
	if len(toks) == 1 {
		return append(s[:t.index], s[t.index+1:]...)
	}
	s[t.index] = deleteAt(s[t.index], toks[1:])
	return s
}

// deepMerge recursively merges src into dst.
func deepMerge(dst, src map[string]interface{}) {
	for k, sv := range src {
		if dv, ok := dst[k]; ok {
			dm, ok1 := dv.(map[string]interface{})
			sm, ok2 := sv.(map[string]interface{})
			if ok1 && ok2 {
				deepMerge(dm, sm)
				continue
			}
		}
		dst[k] = sv
	}
}

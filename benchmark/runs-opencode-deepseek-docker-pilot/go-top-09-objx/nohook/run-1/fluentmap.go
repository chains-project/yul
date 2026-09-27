// Package fluentmap provides a fluent, chainable wrapper around arbitrary
// map[string]interface{} values for convenient reading and mutation of
// dynamic data such as decoded JSON.
package fluentmap

import (
	"encoding/json"
	"errors"
	"strconv"
)

// ErrNotFound is returned by the error-returning helpers when a path cannot be
// resolved.
var ErrNotFound = errors.New("fluentmap: path not found")

// Map wraps a map[string]interface{} and exposes chainable accessors and
// mutators. A nil *Map is safe to read from (behaves as empty) but must be
// created with New or From before it can be mutated.
type Map struct {
	data map[string]interface{}
}

// New returns a Map wrapping m. If no map (or a nil map) is supplied an empty
// Map is returned. The provided map is used directly, not copied.
func New(m ...map[string]interface{}) *Map {
	if len(m) == 0 || m[0] == nil {
		return &Map{data: map[string]interface{}{}}
	}
	return &Map{data: m[0]}
}

// From is an alias for New.
func From(m map[string]interface{}) *Map {
	return New(m)
}

// FromJSON decodes JSON into a new Map. The top-level JSON value must be an
// object.
func FromJSON(b []byte) (*Map, error) {
	m := New()
	if err := json.Unmarshal(b, &m.data); err != nil {
		return nil, err
	}
	return m, nil
}

// FromJSONString is like FromJSON but takes a string.
func FromJSONString(s string) (*Map, error) {
	return FromJSON([]byte(s))
}

// Raw returns the underlying map. Mutating it mutates the Map.
func (m *Map) Raw() map[string]interface{} {
	if m == nil {
		return nil
	}
	return m.data
}

// Len reports the number of top-level keys.
func (m *Map) Len() int {
	if m == nil {
		return 0
	}
	return len(m.data)
}

// Keys returns the top-level keys. Order is not defined.
func (m *Map) Keys() []string {
	if m == nil || len(m.data) == 0 {
		return nil
	}
	keys := make([]string, 0, len(m.data))
	for k := range m.data {
		keys = append(keys, k)
	}
	return keys
}

// Get resolves a dotted path and returns the value found there wrapped in a
// Map. Path segments address nested objects; numeric segments also address
// slice elements. A missing path yields an empty Map so chaining stays safe.
func (m *Map) Get(path string) *Map {
	v, ok := m.Lookup(path)
	if !ok {
		return New()
	}
	child, ok := v.(map[string]interface{})
	if !ok {
		return New()
	}
	return New(child)
}

// Lookup resolves a dotted path and reports whether it exists.
func (m *Map) Lookup(path string) (interface{}, bool) {
	if m == nil || m.data == nil {
		return nil, false
	}
	if path == "" {
		return m.data, true
	}
	var cur interface{} = m.data
	for _, part := range splitPath(path) {
		switch node := cur.(type) {
		case map[string]interface{}:
			v, ok := node[part]
			if !ok {
				return nil, false
			}
			cur = v
		case []interface{}:
			i, err := strconv.Atoi(part)
			if err != nil || i < 0 || i >= len(node) {
				return nil, false
			}
			cur = node[i]
		default:
			return nil, false
		}
	}
	return cur, true
}

// Value resolves path and returns the raw value, or nil when missing.
func (m *Map) Value(path string) interface{} {
	v, _ := m.Lookup(path)
	return v
}

// Exists reports whether path resolves.
func (m *Map) Exists(path string) bool {
	_, ok := m.Lookup(path)
	return ok
}

// String resolves path and returns it as a string. Non-string scalars are
// formatted; a missing path returns "".
func (m *Map) String(path string) string {
	v, ok := m.Lookup(path)
	if !ok {
		return ""
	}
	return ToString(v)
}

// Int resolves path and converts it to an int. A missing or unparsable value
// returns 0.
func (m *Map) Int(path string) int {
	v, _ := m.Lookup(path)
	n, _ := ToInt64(v)
	return int(n)
}

// Int64 resolves path and converts it to an int64. A missing or unparsable
// value returns 0.
func (m *Map) Int64(path string) int64 {
	v, _ := m.Lookup(path)
	n, _ := ToInt64(v)
	return n
}

// Float resolves path and converts it to a float64. A missing or unparsable
// value returns 0.
func (m *Map) Float(path string) float64 {
	v, _ := m.Lookup(path)
	f, _ := ToFloat64(v)
	return f
}

// Bool resolves path and converts it to a bool. A missing or unparsable value
// returns false.
func (m *Map) Bool(path string) bool {
	v, _ := m.Lookup(path)
	b, _ := ToBool(v)
	return b
}

// Slice resolves path and returns it as a slice, or nil when missing.
func (m *Map) Slice(path string) []interface{} {
	v, _ := m.Lookup(path)
	s, _ := v.([]interface{})
	return s
}

// Map resolves path and returns it as a map, or nil when missing.
func (m *Map) Map(path string) map[string]interface{} {
	v, _ := m.Lookup(path)
	mm, _ := v.(map[string]interface{})
	return mm
}

// Set assigns value at path and returns the receiver for chaining. Missing
// intermediate objects are created. Only object segments are traversed when
// writing; use Slice for index access.
func (m *Map) Set(path string, value interface{}) *Map {
	if m.data == nil {
		m.data = map[string]interface{}{}
	}
	if path == "" {
		if vm, ok := value.(map[string]interface{}); ok {
			m.data = vm
		}
		return m
	}
	parts := splitPath(path)
	cur := m.data
	for i, part := range parts {
		if i == len(parts)-1 {
			cur[part] = value
			break
		}
		next, ok := cur[part].(map[string]interface{})
		if !ok {
			next = map[string]interface{}{}
			cur[part] = next
		}
		cur = next
	}
	return m
}

// Delete removes the value at path and returns the receiver for chaining.
func (m *Map) Delete(path string) *Map {
	if m == nil || m.data == nil {
		return m
	}
	if path == "" {
		m.data = map[string]interface{}{}
		return m
	}
	parts := splitPath(path)
	cur := m.data
	for _, part := range parts[:len(parts)-1] {
		next, ok := cur[part].(map[string]interface{})
		if !ok {
			return m
		}
		cur = next
	}
	delete(cur, parts[len(parts)-1])
	return m
}

// Merge deep-merges the supplied maps into the receiver and returns it for
// chaining. Later maps win; nested objects are merged recursively.
func (m *Map) Merge(others ...map[string]interface{}) *Map {
	if m.data == nil {
		m.data = map[string]interface{}{}
	}
	for _, other := range others {
		deepMerge(m.data, other)
	}
	return m
}

// Clone returns a deep copy of the Map.
func (m *Map) Clone() *Map {
	return New(cloneObject(m.data))
}

// MarshalJSON implements json.Marshaler.
func (m *Map) MarshalJSON() ([]byte, error) {
	if m == nil || m.data == nil {
		return []byte("{}"), nil
	}
	return json.Marshal(m.data)
}

// UnmarshalJSON implements json.Unmarshaler.
func (m *Map) UnmarshalJSON(b []byte) error {
	return json.Unmarshal(b, &m.data)
}

// JSON encodes the Map as compact JSON.
func (m *Map) JSON() ([]byte, error) {
	return m.MarshalJSON()
}

// JSONString encodes the Map as a compact JSON string.
func (m *Map) JSONString() (string, error) {
	b, err := m.MarshalJSON()
	if err != nil {
		return "", err
	}
	return string(b), nil
}

// ToString converts common scalar types to their string form.
func ToString(v interface{}) string {
	switch t := v.(type) {
	case nil:
		return ""
	case string:
		return t
	case []byte:
		return string(t)
	case bool:
		return strconv.FormatBool(t)
	case float64:
		return strconv.FormatFloat(t, 'f', -1, 64)
	case float32:
		return strconv.FormatFloat(float64(t), 'f', -1, 32)
	case int:
		return strconv.Itoa(t)
	case int64:
		return strconv.FormatInt(t, 10)
	case json.Number:
		return t.String()
	default:
		return ""
	}
}

// ToInt64 converts common numeric and string types to an int64.
func ToInt64(v interface{}) (int64, error) {
	switch t := v.(type) {
	case int:
		return int64(t), nil
	case int8:
		return int64(t), nil
	case int16:
		return int64(t), nil
	case int32:
		return int64(t), nil
	case int64:
		return t, nil
	case uint:
		return int64(t), nil
	case uint8:
		return int64(t), nil
	case uint16:
		return int64(t), nil
	case uint32:
		return int64(t), nil
	case uint64:
		return int64(t), nil
	case float32:
		return int64(t), nil
	case float64:
		return int64(t), nil
	case json.Number:
		return t.Int64()
	case string:
		return strconv.ParseInt(t, 10, 64)
	default:
		return 0, ErrNotFound
	}
}

// ToFloat64 converts common numeric and string types to a float64.
func ToFloat64(v interface{}) (float64, error) {
	switch t := v.(type) {
	case float64:
		return t, nil
	case float32:
		return float64(t), nil
	case int:
		return float64(t), nil
	case int8:
		return float64(t), nil
	case int16:
		return float64(t), nil
	case int32:
		return float64(t), nil
	case int64:
		return float64(t), nil
	case uint:
		return float64(t), nil
	case uint8:
		return float64(t), nil
	case uint16:
		return float64(t), nil
	case uint32:
		return float64(t), nil
	case uint64:
		return float64(t), nil
	case json.Number:
		return t.Float64()
	case string:
		return strconv.ParseFloat(t, 64)
	default:
		return 0, ErrNotFound
	}
}

// ToBool converts common boolean and string types to a bool.
func ToBool(v interface{}) (bool, error) {
	switch t := v.(type) {
	case bool:
		return t, nil
	case string:
		return strconv.ParseBool(t)
	case json.Number:
		n, err := t.Int64()
		return n != 0, err
	case int:
		return t != 0, nil
	case int64:
		return t != 0, nil
	case float64:
		return t != 0, nil
	default:
		return false, ErrNotFound
	}
}

func splitPath(path string) []string {
	if path == "" {
		return nil
	}
	var parts []string
	start := 0
	for i := 0; i < len(path); i++ {
		if path[i] == '.' {
			parts = append(parts, path[start:i])
			start = i + 1
		}
	}
	parts = append(parts, path[start:])
	return parts
}

func deepMerge(dst, src map[string]interface{}) {
	for k, sv := range src {
		if dv, ok := dst[k]; ok {
			dm, dok := dv.(map[string]interface{})
			sm, sok := sv.(map[string]interface{})
			if dok && sok {
				deepMerge(dm, sm)
				continue
			}
		}
		dst[k] = sv
	}
}

func cloneObject(src map[string]interface{}) map[string]interface{} {
	if src == nil {
		return map[string]interface{}{}
	}
	dst := make(map[string]interface{}, len(src))
	for k, v := range src {
		dst[k] = cloneValue(v)
	}
	return dst
}

func cloneValue(v interface{}) interface{} {
	switch t := v.(type) {
	case map[string]interface{}:
		return cloneObject(t)
	case []interface{}:
		cp := make([]interface{}, len(t))
		for i, e := range t {
			cp[i] = cloneValue(e)
		}
		return cp
	default:
		return v
	}
}

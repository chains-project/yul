// Package mapx provides a fluent, chainable wrapper around arbitrary
// map[string]interface{} data.
//
// A Map is created from an existing map with Of, decoded from JSON with
// FromJSON or FromJSONString, built from a struct with FromStruct, or allocated
// empty with New. Every mutating and transforming method returns a Map so calls
// can be chained:
//
//	result := mapx.Of(data).
//		Set("active", true).
//		SetPath("profile.name", "Ada").
//		Only("id", "active", "profile")
//
// Values are coerced on demand by the typed accessors, so JSON numbers, strings
// and booleans can be read without worrying about the concrete Go type.
package mapx

import (
	"sort"
	"time"
)

// Map is a convenience wrapper around map[string]interface{} exposing a fluent
// API for reading and mutating arbitrary JSON-like data.
type Map map[string]interface{}

// New returns an empty, non-nil Map.
func New() Map {
	return Map{}
}

// Of wraps an existing map. The returned Map shares the underlying storage, so
// mutations are visible through both. A nil map yields an empty Map.
func Of(m map[string]interface{}) Map {
	if m == nil {
		return Map{}
	}
	return Map(m)
}

// Raw returns the underlying map.
func (m Map) Raw() map[string]interface{} {
	return map[string]interface{}(m)
}

// Len reports the number of top-level entries.
func (m Map) Len() int {
	return len(m)
}

// IsEmpty reports whether the map has no entries.
func (m Map) IsEmpty() bool {
	return len(m) == 0
}

// Get returns the value stored at key, or nil if absent.
func (m Map) Get(key string) interface{} {
	if m == nil {
		return nil
	}
	return m[key]
}

// GetOk returns the value stored at key and whether it was present.
func (m Map) GetOk(key string) (interface{}, bool) {
	if m == nil {
		return nil, false
	}
	v, ok := m[key]
	return v, ok
}

// Has reports whether key is present (even if its value is nil).
func (m Map) Has(key string) bool {
	_, ok := m[key]
	return ok
}

// Set stores value at key and returns the map for chaining.
func (m Map) Set(key string, value interface{}) Map {
	m[key] = value
	return m
}

// Delete removes key and returns the map for chaining.
func (m Map) Delete(key string) Map {
	if m != nil {
		delete(m, key)
	}
	return m
}

// Keys returns the top-level keys in ascending order.
func (m Map) Keys() []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

// Values returns the top-level values ordered by their key.
func (m Map) Values() []interface{} {
	keys := m.Keys()
	out := make([]interface{}, 0, len(keys))
	for _, k := range keys {
		out = append(out, m[k])
	}
	return out
}

// Only returns a new Map containing just the given keys that are present.
func (m Map) Only(keys ...string) Map {
	out := make(Map, len(keys))
	for _, k := range keys {
		if v, ok := m[k]; ok {
			out[k] = v
		}
	}
	return out
}

// Except returns a new Map with the given keys removed.
func (m Map) Except(keys ...string) Map {
	drop := make(map[string]struct{}, len(keys))
	for _, k := range keys {
		drop[k] = struct{}{}
	}
	out := make(Map, len(m))
	for k, v := range m {
		if _, skip := drop[k]; !skip {
			out[k] = v
		}
	}
	return out
}

// Filter returns a new Map with the entries for which fn returns true.
func (m Map) Filter(fn func(key string, value interface{}) bool) Map {
	out := make(Map, len(m))
	for k, v := range m {
		if fn(k, v) {
			out[k] = v
		}
	}
	return out
}

// Reject returns a new Map with the entries for which fn returns false.
func (m Map) Reject(fn func(key string, value interface{}) bool) Map {
	out := make(Map, len(m))
	for k, v := range m {
		if !fn(k, v) {
			out[k] = v
		}
	}
	return out
}

// Transform returns a new Map with every value replaced by fn's result.
func (m Map) Transform(fn func(key string, value interface{}) interface{}) Map {
	out := make(Map, len(m))
	for k, v := range m {
		out[k] = fn(k, v)
	}
	return out
}

// MapKeys returns a new Map whose keys are produced by fn.
func (m Map) MapKeys(fn func(key string, value interface{}) string) Map {
	out := make(Map, len(m))
	for k, v := range m {
		out[fn(k, v)] = v
	}
	return out
}

// Each calls fn for every entry and returns the map for chaining.
func (m Map) Each(fn func(key string, value interface{})) Map {
	for k, v := range m {
		fn(k, v)
	}
	return m
}

// Merge copies the top-level entries of the given maps into m (last wins) and
// returns m for chaining.
func (m Map) Merge(others ...map[string]interface{}) Map {
	for _, other := range others {
		for k, v := range other {
			m[k] = v
		}
	}
	return m
}

// MergeRecursive deep-merges the given maps into m and returns m. Nested maps
// are merged entry by entry; non-map values are overwritten (last wins).
func (m Map) MergeRecursive(others ...map[string]interface{}) Map {
	for _, other := range others {
		mergeInto(m, other)
	}
	return m
}

// Clean returns a new Map without nil values and empty strings, slices and maps.
func (m Map) Clean() Map {
	out := make(Map, len(m))
	for k, v := range m {
		switch x := v.(type) {
		case nil:
			continue
		case string:
			if x == "" {
				continue
			}
		case []interface{}:
			if len(x) == 0 {
				continue
			}
		case map[string]interface{}:
			if len(x) == 0 {
				continue
			}
		}
		out[k] = v
	}
	return out
}

// Clone returns a deep copy of m. Nested maps and slices are copied
// recursively; leaf values are copied by assignment.
func (m Map) Clone() Map {
	return Map(cloneMap(m))
}

func cloneMap(m Map) map[string]interface{} {
	out := make(map[string]interface{}, len(m))
	for k, v := range m {
		out[k] = cloneValue(v)
	}
	return out
}

func cloneValue(v interface{}) interface{} {
	switch x := v.(type) {
	case Map:
		return cloneMap(x)
	case map[string]interface{}:
		return cloneMap(x)
	case []interface{}:
		out := make([]interface{}, len(x))
		for i := range x {
			out[i] = cloneValue(x[i])
		}
		return out
	default:
		return v
	}
}

func mergeInto(dst, src map[string]interface{}) {
	for k, v := range src {
		dv, dstIsMap := toMap(dst[k])
		sv, srcIsMap := toMap(v)
		if dstIsMap && srcIsMap {
			mergeInto(dv, sv)
			continue
		}
		dst[k] = v
	}
}

// GetString returns the value at key coerced to a string, or "" if absent or
// not convertible.
func (m Map) GetString(key string) string {
	v, _ := toString(m.Get(key))
	return v
}

// GetInt returns the value at key coerced to an int, or 0 if absent or not
// convertible.
func (m Map) GetInt(key string) int {
	v, _ := toInt64(m.Get(key))
	return int(v)
}

// GetInt64 returns the value at key coerced to an int64, or 0 if absent or not
// convertible.
func (m Map) GetInt64(key string) int64 {
	v, _ := toInt64(m.Get(key))
	return v
}

// GetFloat64 returns the value at key coerced to a float64, or 0 if absent or
// not convertible.
func (m Map) GetFloat64(key string) float64 {
	v, _ := toFloat64(m.Get(key))
	return v
}

// GetBool returns the value at key coerced to a bool, or false if absent or not
// convertible.
func (m Map) GetBool(key string) bool {
	v, _ := toBool(m.Get(key))
	return v
}

// GetMap returns the value at key as a Map. It returns an empty Map if the
// value is absent or not a string-keyed map.
func (m Map) GetMap(key string) Map {
	if mm, ok := toMap(m.Get(key)); ok {
		return mm
	}
	return Map{}
}

// GetSlice returns the value at key as a []interface{}. It returns nil if the
// value is absent or not a slice or array.
func (m Map) GetSlice(key string) []interface{} {
	v, _ := toSlice(m.Get(key))
	return v
}

// GetStrings returns the value at key as a []string, coercing each element. It
// returns nil if the value is absent or not a slice or array.
func (m Map) GetStrings(key string) []string {
	slice, ok := toSlice(m.Get(key))
	if !ok {
		return nil
	}
	out := make([]string, 0, len(slice))
	for _, v := range slice {
		s, _ := toString(v)
		out = append(out, s)
	}
	return out
}

// GetTime returns the value at key parsed as a time.Time. Accepted inputs are
// time.Time, Unix timestamps (numeric), and common string layouts such as
// RFC3339.
func (m Map) GetTime(key string) time.Time {
	v, _ := toTime(m.Get(key))
	return v
}

// GetDuration returns the value at key parsed as a time.Duration. Accepted
// inputs are time.Duration, duration strings ("1h30m") and numeric
// nanosecond counts.
func (m Map) GetDuration(key string) time.Duration {
	v, _ := toDuration(m.Get(key))
	return v
}

// GetOr returns the value at key if present and non-nil, otherwise def.
func (m Map) GetOr(key string, def interface{}) interface{} {
	if v, ok := m.GetOk(key); ok && v != nil {
		return v
	}
	return def
}

// String returns the JSON encoding of the map. It returns "" if the map cannot
// be encoded.
func (m Map) String() string {
	s, err := m.Encode()
	if err != nil {
		return ""
	}
	return s
}

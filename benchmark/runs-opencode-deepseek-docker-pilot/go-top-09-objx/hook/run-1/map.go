package mapq

import (
	"fmt"
	"sort"
)

// Map is a fluent, chainable wrapper around a map[string]interface{}.
//
// Mutating methods return the receiver so calls can be chained. Any error
// encountered while traversing a path is latched and reported by Err; once an
// error is latched, subsequent mutations become no-ops so a chain cannot
// silently operate on a partially built value.
type Map struct {
	data map[string]interface{}
	err  error
}

// New returns a Map. When data is provided and non-nil the returned Map wraps
// it directly (it is not copied); otherwise the Map is backed by a fresh empty
// map. Multiple arguments are ignored after the first.
func New(data ...map[string]interface{}) *Map {
	m := &Map{data: map[string]interface{}{}}
	if len(data) > 0 && data[0] != nil {
		m.data = data[0]
	}
	return m
}

// Wrap is an alias for New that reads more naturally when converting an
// existing map into a Map.
func Wrap(data map[string]interface{}) *Map { return New(data) }

// Data returns the underlying map. The returned map is not a copy and remains
// owned by the Map.
func (m *Map) Data() map[string]interface{} { return m.data }

// Err reports the first traversal error encountered by a mutating method. It
// returns nil when the chain is healthy.
func (m *Map) Err() error { return m.err }

// ErrOrNil returns the Map when no error has been latched, otherwise it returns
// nil together with that error.
func (m *Map) ErrOrNil() (*Map, error) {
	if m.err != nil {
		return nil, m.err
	}
	return m, nil
}

// Done returns the Map and its latched error, which reads naturally at the end
// of a chain:
//
//	m, err := mapq.New().Set("a.b", 1).Done()
func (m *Map) Done() (*Map, error) { return m, m.err }

func (m *Map) fail(err error) *Map {
	if m.err == nil {
		m.err = err
	}
	return m
}

// Get returns the value at path and reports whether it exists, including
// explicit nil values.
func (m *Map) Get(path string) (interface{}, bool) {
	tokens, err := parsePath(path)
	if err != nil {
		return nil, false
	}
	return getValue(m.data, tokens)
}

// GetOr returns the value at path, or fallback when the path is absent.
func (m *Map) GetOr(path string, fallback interface{}) interface{} {
	if v, ok := m.Get(path); ok {
		return v
	}
	return fallback
}

// Set assigns value at path, creating intermediate maps and slices as needed.
// Numeric segments address slice elements and grow the slice on demand.
func (m *Map) Set(path string, value interface{}) *Map {
	if m.err != nil {
		return m
	}
	tokens, err := parsePath(path)
	if err != nil {
		return m.fail(err)
	}
	if len(tokens) == 0 {
		return m.fail(fmt.Errorf("mapq: cannot set the root; use SetPath or Merge"))
	}
	if m.data == nil {
		m.data = map[string]interface{}{}
	}
	result, err := setValue(m.data, tokens, value)
	if err != nil {
		return m.fail(err)
	}
	if mm, ok := result.(map[string]interface{}); ok {
		m.data = mm
	}
	return m
}

// SetPath is an alias for Set.
func (m *Map) SetPath(path string, value interface{}) *Map { return m.Set(path, value) }

// Delete removes the value at path. Removing a slice element shifts the
// remaining elements down, so subsequent indices change.
func (m *Map) Delete(path string) *Map {
	if m.err != nil {
		return m
	}
	tokens, err := parsePath(path)
	if err != nil {
		return m.fail(err)
	}
	if len(tokens) == 0 {
		return m
	}
	result, deleted, err := deleteValue(m.data, tokens)
	if err != nil {
		return m.fail(err)
	}
	if deleted {
		if mm, ok := result.(map[string]interface{}); ok {
			m.data = mm
		}
	}
	return m
}

// Has reports whether path resolves to a value, including explicit nil values.
func (m *Map) Has(path string) bool {
	_, ok := m.Get(path)
	return ok
}

// Exists is an alias for Has.
func (m *Map) Exists(path string) bool { return m.Has(path) }

// Update replaces the value at path with the result of fn applied to the
// current value. When the path is absent, fn receives nil.
func (m *Map) Update(path string, fn func(current interface{}) interface{}) *Map {
	if m.err != nil {
		return m
	}
	current, _ := m.Get(path)
	return m.Set(path, fn(current))
}

// Apply runs fn with the receiver and returns its result, allowing arbitrary
// logic to be embedded in a chain. A nil result leaves the receiver unchanged.
func (m *Map) Apply(fn func(*Map) *Map) *Map {
	if out := fn(m); out != nil {
		return out
	}
	return m
}

// Len returns the number of keys at the top level.
func (m *Map) Len() int { return len(m.data) }

// Keys returns the top-level keys sorted lexicographically.
func (m *Map) Keys() []string {
	keys := make([]string, 0, len(m.data))
	for k := range m.data {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

// ForEach calls fn for every top-level key in sorted order. Returning false
// stops iteration. Both the receiver and fn may mutate the map.
func (m *Map) ForEach(fn func(key string, value interface{}) bool) *Map {
	for _, k := range m.Keys() {
		if !fn(k, m.data[k]) {
			break
		}
	}
	return m
}

// Clone returns a deep copy of the Map. Nested maps and slices are copied
// recursively; other values are copied by reference.
func (m *Map) Clone() *Map {
	return &Map{data: cloneValue(m.data).(map[string]interface{})}
}

// Merge deep-merges other into the receiver and returns the receiver. Nested
// maps are merged recursively; any other value (including slices) is replaced.
func (m *Map) Merge(other *Map) *Map {
	if m.err != nil || other == nil {
		return m
	}
	if m.data == nil {
		m.data = map[string]interface{}{}
	}
	mergeValue(m.data, other.data)
	return m
}

// Sub returns the nested map at path as a Map. When the path is absent or does
// not hold a map, an empty Map is returned so the value can still be chained.
func (m *Map) Sub(path string) *Map {
	if v, ok := m.Get(path); ok {
		if mm, ok := asMap(v); ok {
			return &Map{data: mm}
		}
	}
	return New()
}

// Map returns the nested map at path and whether it was present and map-shaped.
func (m *Map) Map(path string) (*Map, bool) {
	v, ok := m.Get(path)
	if !ok {
		return nil, false
	}
	mm, ok := asMap(v)
	if !ok {
		return nil, false
	}
	return &Map{data: mm}, true
}

// getValue walks tokens through nested maps and slices without mutating them.
func getValue(container interface{}, tokens []token) (interface{}, bool) {
	if len(tokens) == 0 {
		return container, true
	}
	t := tokens[0]
	if t.isIndex {
		slice, ok := container.([]interface{})
		if !ok || t.index < 0 || t.index >= len(slice) {
			return nil, false
		}
		return getValue(slice[t.index], tokens[1:])
	}
	mp, ok := asMap(container)
	if !ok {
		return nil, false
	}
	v, ok := mp[t.key]
	if !ok {
		return nil, false
	}
	return getValue(v, tokens[1:])
}

// setValue returns container with value placed at tokens, creating intermediate
// maps and slices. The returned value must replace the caller's reference to
// container because slices may be reallocated.
func setValue(container interface{}, tokens []token, value interface{}) (interface{}, error) {
	if len(tokens) == 0 {
		return value, nil
	}
	t := tokens[0]
	if t.isIndex {
		slice, _ := container.([]interface{})
		if container != nil {
			if _, ok := container.([]interface{}); !ok {
				return nil, fmt.Errorf("mapq: cannot use index on %T", container)
			}
		}
		for len(slice) <= t.index {
			slice = append(slice, nil)
		}
		child, err := setValue(slice[t.index], tokens[1:], value)
		if err != nil {
			return nil, err
		}
		slice[t.index] = child
		return slice, nil
	}

	mp, ok := asMap(container)
	if !ok {
		if container != nil {
			return nil, fmt.Errorf("mapq: cannot use key %q on %T", t.key, container)
		}
		mp = map[string]interface{}{}
	}
	if mp == nil {
		mp = map[string]interface{}{}
	}
	child, err := setValue(mp[t.key], tokens[1:], value)
	if err != nil {
		return nil, err
	}
	mp[t.key] = child
	return mp, nil
}

// deleteValue removes the value at tokens, returning the possibly-updated
// container and whether anything was removed.
func deleteValue(container interface{}, tokens []token) (interface{}, bool, error) {
	if len(tokens) == 0 {
		return container, false, nil
	}
	t := tokens[0]
	if t.isIndex {
		slice, ok := container.([]interface{})
		if !ok || t.index < 0 || t.index >= len(slice) {
			return container, false, nil
		}
		if len(tokens) == 1 {
			return append(slice[:t.index], slice[t.index+1:]...), true, nil
		}
		child, deleted, err := deleteValue(slice[t.index], tokens[1:])
		if err != nil {
			return container, false, err
		}
		if deleted {
			slice[t.index] = child
		}
		return slice, deleted, nil
	}
	mp, ok := asMap(container)
	if !ok {
		return container, false, nil
	}
	if len(tokens) == 1 {
		if _, exists := mp[t.key]; !exists {
			return container, false, nil
		}
		delete(mp, t.key)
		return mp, true, nil
	}
	child, deleted, err := deleteValue(mp[t.key], tokens[1:])
	if err != nil {
		return container, false, err
	}
	if deleted {
		mp[t.key] = child
	}
	return mp, deleted, nil
}

// asMap normalizes the common map shapes to map[string]interface{}.
func asMap(v interface{}) (map[string]interface{}, bool) {
	mm, ok := v.(map[string]interface{})
	return mm, ok
}

// cloneValue recursively copies maps and slices.
func cloneValue(v interface{}) interface{} {
	switch val := v.(type) {
	case map[string]interface{}:
		out := make(map[string]interface{}, len(val))
		for k, child := range val {
			out[k] = cloneValue(child)
		}
		return out
	case []interface{}:
		out := make([]interface{}, len(val))
		for i, child := range val {
			out[i] = cloneValue(child)
		}
		return out
	default:
		return v
	}
}

// mergeValue deep-merges src into dst in place. Nested maps are merged; all
// other values from src replace those in dst.
func mergeValue(dst, src map[string]interface{}) {
	for k, sv := range src {
		if dv, ok := dst[k]; ok {
			dstMap, dok := dv.(map[string]interface{})
			srcMap, sok := sv.(map[string]interface{})
			if dok && sok {
				mergeValue(dstMap, srcMap)
				continue
			}
		}
		dst[k] = cloneValue(sv)
	}
}

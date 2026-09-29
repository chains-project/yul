package mapfluent

import "sort"

// Map wraps an arbitrary JSON-like value and exposes a fluent, chainable API
// for reading and mutating nested map[string]interface{} data.
//
// The zero value is not usable directly; construct one with New, Wrap, or
// FromJSON. A *Map is safe for chaining: methods never return nil, so a call
// on a missing key still produces a usable (nil-valued) Map.
type Map struct {
	value interface{}
	found bool
}

// New returns a Map backed by the supplied object. With no argument (or a nil
// argument) it starts from an empty object. The supplied map is used directly,
// not copied.
func New(data ...map[string]interface{}) *Map {
	m := map[string]interface{}{}
	if len(data) > 0 && data[0] != nil {
		m = data[0]
	}
	return &Map{value: m, found: true}
}

// Wrap returns a Map around an arbitrary value, which may be an object, an
// array, a scalar, or nil.
func Wrap(value interface{}) *Map {
	return &Map{value: value, found: true}
}

// Clone returns a deep copy of the Map. Mutating the clone never affects the
// original, and vice versa.
func (m *Map) Clone() *Map {
	return &Map{value: deepClone(m.value), found: m.found}
}

// Value returns the underlying value.
func (m *Map) Value() interface{} {
	if m == nil {
		return nil
	}
	return m.value
}

// Interface is an alias for Value.
func (m *Map) Interface() interface{} {
	return m.Value()
}

// Raw is an alias for Value.
func (m *Map) Raw() interface{} {
	return m.Value()
}

// Map is an alias for Object.
func (m *Map) Map() map[string]interface{} {
	return m.Object()
}

// Object returns the underlying value if it is an object, otherwise nil.
func (m *Map) Object() map[string]interface{} {
	if m == nil {
		return nil
	}
	if obj, ok := m.value.(map[string]interface{}); ok {
		return obj
	}
	return nil
}

// Array returns the underlying value as a slice if it is an array, otherwise
// nil.
func (m *Map) Array() []interface{} {
	if m == nil {
		return nil
	}
	if arr, ok := m.value.([]interface{}); ok {
		return arr
	}
	return nil
}

// Exists reports whether the wrapped value was present. A present but
// explicitly nil value reports true; a missing key reports false.
func (m *Map) Exists() bool {
	return m != nil && m.found
}

// IsNil reports whether the wrapped value is nil.
func (m *Map) IsNil() bool {
	return m == nil || m.value == nil
}

// IsObject reports whether the wrapped value is an object.
func (m *Map) IsObject() bool {
	_, ok := m.Value().(map[string]interface{})
	return ok
}

// IsArray reports whether the wrapped value is an array.
func (m *Map) IsArray() bool {
	_, ok := m.Value().([]interface{})
	return ok
}

// Get returns the value of the given key, or of successive nested keys when
// several are supplied. Each argument is treated as a literal key.
func (m *Map) Get(keys ...string) *Map {
	value, ok := lookup(m.Value(), keys)
	return &Map{value: value, found: ok}
}

// GetPath is like Get but splits a single dotted path into keys, with optional
// zero-based array indexes written in brackets. For example "user.langs[0].name".
func (m *Map) GetPath(path string) *Map {
	return m.Get(parsePath(path)...)
}

// At is an alias for Get.
func (m *Map) At(keys ...string) *Map {
	return m.Get(keys...)
}

// Set assigns value to the top-level key and returns the receiver for
// chaining. If the Map is not currently an object it is replaced by a new one.
func (m *Map) Set(key string, value interface{}) *Map {
	root, _ := setPath(m.value, []string{key}, value)
	m.value = root
	m.found = true
	return m
}

// SetPath assigns value at the given dotted path, creating intermediate
// objects as needed, and returns the receiver for chaining.
func (m *Map) SetPath(path string, value interface{}) *Map {
	root, _ := setPath(m.value, parsePath(path), value)
	m.value = root
	m.found = true
	return m
}

// SetAll copies every key from src into the receiver at the top level and
// returns the receiver for chaining.
func (m *Map) SetAll(src map[string]interface{}) *Map {
	obj := m.object()
	for k, v := range src {
		obj[k] = v
	}
	return m
}

// Delete removes the top-level key and returns the receiver for chaining.
func (m *Map) Delete(key string) *Map {
	if root, ok := deletePath(m.value, []string{key}); ok {
		m.value = root
	}
	return m
}

// DeletePath removes the value at the given dotted path and returns the
// receiver for chaining.
func (m *Map) DeletePath(path string) *Map {
	if root, ok := deletePath(m.value, parsePath(path)); ok {
		m.value = root
	}
	return m
}

// Has reports whether the top-level key is present.
func (m *Map) Has(key string) bool {
	_, ok := lookup(m.Value(), []string{key})
	return ok
}

// HasPath reports whether the dotted path is present.
func (m *Map) HasPath(path string) bool {
	_, ok := lookup(m.value, parsePath(path))
	return ok
}

// Keys returns the sorted top-level keys of an object, or the string indexes
// of an array. It returns nil for any other value.
func (m *Map) Keys() []string {
	switch v := m.Value().(type) {
	case map[string]interface{}:
		keys := make([]string, 0, len(v))
		for k := range v {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		return keys
	case []interface{}:
		keys := make([]string, len(v))
		for i := range v {
			keys[i] = itoa(i)
		}
		return keys
	default:
		return nil
	}
}

// Len returns the number of elements in an object or array, zero otherwise.
func (m *Map) Len() int {
	switch v := m.Value().(type) {
	case map[string]interface{}:
		return len(v)
	case []interface{}:
		return len(v)
	default:
		return 0
	}
}

// Each calls fn for every top-level entry of an object in sorted key order.
// Iteration stops early when fn returns false. It returns the receiver for
// chaining.
func (m *Map) Each(fn func(key string, value *Map) bool) *Map {
	obj := m.Object()
	if obj == nil {
		return m
	}
	for _, key := range m.Keys() {
		if !fn(key, Wrap(obj[key])) {
			break
		}
	}
	return m
}

// Merge deep-merges the supplied maps into the receiver. Nested objects are
// merged recursively; all other values are replaced. It returns the receiver
// for chaining.
func (m *Map) Merge(others ...*Map) *Map {
	dst := m.object()
	for _, other := range others {
		if other == nil {
			continue
		}
		if src := other.Object(); src != nil {
			deepMerge(dst, src)
		}
	}
	return m
}

// object returns the underlying object, replacing the value with a new empty
// object if it is not already one.
func (m *Map) object() map[string]interface{} {
	if obj, ok := m.value.(map[string]interface{}); ok {
		return obj
	}
	obj := map[string]interface{}{}
	m.value = obj
	m.found = true
	return obj
}

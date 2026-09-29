package fluentmap

// The methods in this file are the typed read accessors. They never panic on a
// nil receiver or a missing key; instead they return the zero value.

// String returns the value at key as a string.
func (m *Map) String(key string) string {
	v, _ := m.Get(key)
	return toString(v)
}

// Int returns the value at key as an int64.
func (m *Map) Int(key string) int64 {
	v, _ := m.Get(key)
	i, _ := toInt64(v)
	return i
}

// Float returns the value at key as a float64.
func (m *Map) Float(key string) float64 {
	v, _ := m.Get(key)
	f, _ := toFloat64(v)
	return f
}

// Bool returns the value at key as a bool.
func (m *Map) Bool(key string) bool {
	v, _ := m.Get(key)
	b, _ := toBool(v)
	return b
}

// Map returns the nested object at key as a *Map, or nil if key does not hold
// an object. The returned Map remains linked to the receiver's data.
func (m *Map) Map(key string) *Map {
	nested, ok := m.nestedMap(key)
	if !ok {
		return nil
	}
	return From(nested)
}

// Slice returns the value at key as a []interface{}. A nil slice is returned
// when key is missing or does not hold an array.
func (m *Map) Slice(key string) []interface{} {
	v, ok := m.Get(key)
	if !ok {
		return nil
	}
	s, _ := v.([]interface{})
	return s
}

// Exists reports whether the value at key is non-nil.
func (m *Map) Exists(key string) bool {
	v, ok := m.Get(key)
	return ok && v != nil
}

// StringPath returns the value at the dot-separated path as a string.
func (m *Map) StringPath(path string) string {
	v, _ := m.GetPath(path)
	return toString(v)
}

// IntPath returns the value at the dot-separated path as an int64.
func (m *Map) IntPath(path string) int64 {
	v, _ := m.GetPath(path)
	i, _ := toInt64(v)
	return i
}

// FloatPath returns the value at the dot-separated path as a float64.
func (m *Map) FloatPath(path string) float64 {
	v, _ := m.GetPath(path)
	f, _ := toFloat64(v)
	return f
}

// BoolPath returns the value at the dot-separated path as a bool.
func (m *Map) BoolPath(path string) bool {
	v, _ := m.GetPath(path)
	b, _ := toBool(v)
	return b
}

// MapPath returns the nested object at the dot-separated path as a *Map, or
// nil if the path does not hold an object.
func (m *Map) MapPath(path string) *Map {
	v, ok := m.GetPath(path)
	if !ok {
		return nil
	}
	nested, ok := asMap(v)
	if !ok {
		return nil
	}
	return From(nested)
}

// SlicePath returns the value at the dot-separated path as a []interface{}.
func (m *Map) SlicePath(path string) []interface{} {
	v, ok := m.GetPath(path)
	if !ok {
		return nil
	}
	s, _ := v.([]interface{})
	return s
}

// ExistsPath reports whether the value at the dot-separated path is non-nil.
func (m *Map) ExistsPath(path string) bool {
	v, ok := m.GetPath(path)
	return ok && v != nil
}

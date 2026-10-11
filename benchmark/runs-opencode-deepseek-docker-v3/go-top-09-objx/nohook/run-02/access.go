package fluentmap

// getAs performs a lookup and converts the result with conv.
func getAs[T any](lookup func() (interface{}, bool), conv func(interface{}) (T, bool)) (T, bool) {
	var zero T
	v, ok := lookup()
	if !ok {
		return zero, false
	}
	return conv(v)
}

// GetString returns the value for key converted to a string.
func (m *Map) GetString(key string) (string, bool) {
	return getAs(func() (interface{}, bool) { return m.Get(key) }, toString)
}

// GetInt returns the value for key converted to an int.
func (m *Map) GetInt(key string) (int, bool) {
	return getAs(func() (interface{}, bool) { return m.Get(key) }, toInt)
}

// GetInt64 returns the value for key converted to an int64.
func (m *Map) GetInt64(key string) (int64, bool) {
	return getAs(func() (interface{}, bool) { return m.Get(key) }, toInt64)
}

// GetFloat64 returns the value for key converted to a float64.
func (m *Map) GetFloat64(key string) (float64, bool) {
	return getAs(func() (interface{}, bool) { return m.Get(key) }, toFloat64)
}

// GetBool returns the value for key converted to a bool.
func (m *Map) GetBool(key string) (bool, bool) {
	return getAs(func() (interface{}, bool) { return m.Get(key) }, toBool)
}

// GetSlice returns the value for key as a slice of interface{}.
func (m *Map) GetSlice(key string) ([]interface{}, bool) {
	return getAs(func() (interface{}, bool) { return m.Get(key) }, toSlice)
}

// GetStrings returns the value for key as a []string.
func (m *Map) GetStrings(key string) ([]string, bool) {
	return getAs(func() (interface{}, bool) { return m.Get(key) }, toStrings)
}

// GetMap returns the value for key as a Map. The returned Map wraps the nested
// map, so mutations are shared with the receiver.
func (m *Map) GetMap(key string) (*Map, bool) {
	return getAs(func() (interface{}, bool) { return m.Get(key) }, asMap)
}

// GetPathString returns the value at a dot/bracket path converted to a string.
func (m *Map) GetPathString(path string) (string, bool) {
	return getAs(func() (interface{}, bool) { return m.lookupPath(path) }, toString)
}

// GetPathInt returns the value at a dot/bracket path converted to an int.
func (m *Map) GetPathInt(path string) (int, bool) {
	return getAs(func() (interface{}, bool) { return m.lookupPath(path) }, toInt)
}

// GetPathInt64 returns the value at a dot/bracket path converted to an int64.
func (m *Map) GetPathInt64(path string) (int64, bool) {
	return getAs(func() (interface{}, bool) { return m.lookupPath(path) }, toInt64)
}

// GetPathFloat64 returns the value at a dot/bracket path converted to a float64.
func (m *Map) GetPathFloat64(path string) (float64, bool) {
	return getAs(func() (interface{}, bool) { return m.lookupPath(path) }, toFloat64)
}

// GetPathBool returns the value at a dot/bracket path converted to a bool.
func (m *Map) GetPathBool(path string) (bool, bool) {
	return getAs(func() (interface{}, bool) { return m.lookupPath(path) }, toBool)
}

// GetPathSlice returns the value at a dot/bracket path as a slice.
func (m *Map) GetPathSlice(path string) ([]interface{}, bool) {
	return getAs(func() (interface{}, bool) { return m.lookupPath(path) }, toSlice)
}

// GetPathStrings returns the value at a dot/bracket path as a []string.
func (m *Map) GetPathStrings(path string) ([]string, bool) {
	return getAs(func() (interface{}, bool) { return m.lookupPath(path) }, toStrings)
}

// GetPathMap returns the value at a dot/bracket path as a Map. The returned Map
// wraps the nested map, so mutations are shared with the receiver.
func (m *Map) GetPathMap(path string) (*Map, bool) {
	return getAs(func() (interface{}, bool) { return m.lookupPath(path) }, asMap)
}

func asMap(v interface{}) (*Map, bool) {
	mp, ok := toMap(v)
	if !ok {
		return nil, false
	}
	return From(mp), true
}

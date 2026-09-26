package objx

import (
	"encoding/json"
	"strings"
)

// Map is a map[string]interface{} with a fluent, chainable API for
// accessing and manipulating its data.
type Map map[string]interface{}

// New wraps an existing map[string]interface{} as a Map.
func New(data map[string]interface{}) Map {
	return Map(data)
}

// MSI builds a Map from alternating key/value arguments, e.g.
// MSI("name", "Mat", "age", 30).
func MSI(keyAndValuePairs ...interface{}) Map {
	if len(keyAndValuePairs)%2 != 0 {
		panic("objx: MSI must be given an even number of arguments (key/value pairs)")
	}
	m := Map{}
	for i := 0; i < len(keyAndValuePairs); i += 2 {
		key, ok := keyAndValuePairs[i].(string)
		if !ok {
			panic("objx: MSI keys must be strings")
		}
		m[key] = keyAndValuePairs[i+1]
	}
	return m
}

// FromJSON creates a Map from a JSON object string.
func FromJSON(jsonString string) (Map, error) {
	var m Map
	if err := json.Unmarshal([]byte(jsonString), &m); err != nil {
		return nil, err
	}
	return m, nil
}

// MustFromJSON is like FromJSON but panics on error.
func MustFromJSON(jsonString string) Map {
	m, err := FromJSON(jsonString)
	if err != nil {
		panic(err)
	}
	return m
}

// Get retrieves the value at the dotted-path selector (e.g. "a.b.c"),
// with optional array indices (e.g. "a.items[0].name"). It always
// returns a non-nil *Value; if the path doesn't resolve to anything,
// the returned Value holds nil.
func (m Map) Get(selector string) *Value {
	var current interface{} = m
	for _, part := range strings.Split(selector, ".") {
		if current == nil {
			break
		}
		current = access(current, part)
	}
	return &Value{data: current}
}

// Has reports whether the selector resolves to a non-nil value.
func (m Map) Has(selector string) bool {
	return !m.Get(selector).IsNil()
}

// Keys returns the top-level keys of the map.
func (m Map) Keys() []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}

// JSON marshals the map to a JSON object string.
func (m Map) JSON() (string, error) {
	b, err := json.Marshal(m)
	if err != nil {
		return "", err
	}
	return string(b), nil
}

// MustJSON is like JSON but panics on error.
func (m Map) MustJSON() string {
	s, err := m.JSON()
	if err != nil {
		panic(err)
	}
	return s
}

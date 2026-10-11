package fluentmap

import (
	"encoding/json"
	"errors"
	"fmt"
)

// Parse decodes JSON object data into a new Map.
func Parse(data []byte) (*Map, error) {
	var out map[string]interface{}
	if err := json.Unmarshal(data, &out); err != nil {
		return nil, err
	}
	return From(out), nil
}

// MarshalJSON implements json.Marshaler.
func (m *Map) MarshalJSON() ([]byte, error) {
	if m == nil || m.data == nil {
		return []byte("null"), nil
	}
	return json.Marshal(m.data)
}

// UnmarshalJSON implements json.Unmarshaler, replacing the Map's contents.
func (m *Map) UnmarshalJSON(data []byte) error {
	if m == nil {
		return errors.New("fluentmap: UnmarshalJSON on nil *Map")
	}
	var out map[string]interface{}
	if err := json.Unmarshal(data, &out); err != nil {
		return err
	}
	m.data = out
	return nil
}

// Decode marshals the Map and unmarshals it into v, allowing a Map to populate
// a struct.
func (m *Map) Decode(v interface{}) error {
	data, err := m.MarshalJSON()
	if err != nil {
		return err
	}
	return json.Unmarshal(data, v)
}

// String returns the JSON encoding of the Map, implementing fmt.Stringer. If the
// data cannot be encoded, a fallback representation is returned.
func (m *Map) String() string {
	if m == nil {
		return "null"
	}
	data, err := json.Marshal(m.data)
	if err != nil {
		return fmt.Sprintf("fluentmap.Map%v", m.data)
	}
	return string(data)
}

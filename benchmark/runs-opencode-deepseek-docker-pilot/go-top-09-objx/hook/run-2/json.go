package mapfluent

import "encoding/json"

// FromJSON decodes JSON data into a Map. The decoded value may be an object,
// an array, a scalar, or null.
func FromJSON(data []byte) (*Map, error) {
	var value interface{}
	if err := json.Unmarshal(data, &value); err != nil {
		return nil, err
	}
	return &Map{value: value, found: true}, nil
}

// ToJSON encodes the wrapped value as compact JSON.
func (m *Map) ToJSON() ([]byte, error) {
	return json.Marshal(m.Value())
}

// ToJSONIndent encodes the wrapped value as indented JSON.
func (m *Map) ToJSONIndent(prefix, indent string) ([]byte, error) {
	return json.MarshalIndent(m.Value(), prefix, indent)
}

// JSONString returns the wrapped value as a compact JSON string. It returns ""
// if the value cannot be encoded.
func (m *Map) JSONString() string {
	data, err := m.ToJSON()
	if err != nil {
		return ""
	}
	return string(data)
}

// Decode unmarshals the wrapped value into v using encoding/json. It is handy
// for turning dynamic data into a typed struct.
func (m *Map) Decode(v interface{}) error {
	data, err := m.ToJSON()
	if err != nil {
		return err
	}
	return json.Unmarshal(data, v)
}

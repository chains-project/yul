package mapx

import (
	"encoding/json"
	"errors"
)

// FromJSON decodes a JSON object into a Map.
func FromJSON(data []byte) (Map, error) {
	m := Map{}
	if err := json.Unmarshal(data, &m); err != nil {
		return nil, err
	}
	return m, nil
}

// FromJSONString decodes a JSON object string into a Map.
func FromJSONString(s string) (Map, error) {
	return FromJSON([]byte(s))
}

// FromStruct converts a struct or any JSON-marshalable value into a Map by
// round-tripping through JSON.
func FromStruct(v interface{}) (Map, error) {
	data, err := json.Marshal(v)
	if err != nil {
		return nil, err
	}
	return FromJSON(data)
}

// ToJSON encodes the map as JSON.
func (m Map) ToJSON() ([]byte, error) {
	return json.Marshal(m)
}

// Encode encodes the map as a JSON string.
func (m Map) Encode() (string, error) {
	data, err := json.Marshal(m)
	if err != nil {
		return "", err
	}
	return string(data), nil
}

// Into decodes the map into v using JSON field tags.
func (m Map) Into(v interface{}) error {
	data, err := json.Marshal(m)
	if err != nil {
		return err
	}
	return json.Unmarshal(data, v)
}

// MarshalJSON implements json.Marshaler.
func (m Map) MarshalJSON() ([]byte, error) {
	if m == nil {
		return []byte("null"), nil
	}
	return json.Marshal(map[string]interface{}(m))
}

// UnmarshalJSON implements json.Unmarshaler.
func (m *Map) UnmarshalJSON(data []byte) error {
	if m == nil {
		return errors.New("mapx: UnmarshalJSON on nil *Map")
	}
	var raw map[string]interface{}
	if err := json.Unmarshal(data, &raw); err != nil {
		return err
	}
	*m = raw
	return nil
}

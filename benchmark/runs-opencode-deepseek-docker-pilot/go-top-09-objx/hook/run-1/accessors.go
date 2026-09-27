package mapq

import (
	"encoding/json"
	"fmt"
	"strconv"
)

func first[T any](def []T) T {
	var zero T
	if len(def) > 0 {
		return def[0]
	}
	return zero
}

// String returns the value at path as a string. When the value is absent or
// cannot be represented as a string, the optional default is returned.
func (m *Map) String(path string, def ...string) string {
	if v, ok := m.Get(path); ok {
		if s, ok := toString(v); ok {
			return s
		}
	}
	return first(def)
}

// Bool returns the value at path as a bool, coercing strings via
// strconv.ParseBool and numbers where zero is false.
func (m *Map) Bool(path string, def ...bool) bool {
	if v, ok := m.Get(path); ok {
		if b, ok := toBool(v); ok {
			return b
		}
	}
	return first(def)
}

// Int returns the value at path as an int.
func (m *Map) Int(path string, def ...int) int {
	if v, ok := m.Get(path); ok {
		if n, ok := toInt64(v); ok {
			return int(n)
		}
	}
	return first(def)
}

// Int64 returns the value at path as an int64.
func (m *Map) Int64(path string, def ...int64) int64 {
	if v, ok := m.Get(path); ok {
		if n, ok := toInt64(v); ok {
			return n
		}
	}
	return first(def)
}

// Float64 returns the value at path as a float64.
func (m *Map) Float64(path string, def ...float64) float64 {
	if v, ok := m.Get(path); ok {
		if f, ok := toFloat64(v); ok {
			return f
		}
	}
	return first(def)
}

// Slice returns the value at path as a slice. It returns nil when the path is
// absent or does not hold a slice.
func (m *Map) Slice(path string) []interface{} {
	if v, ok := m.Get(path); ok {
		if s, ok := v.([]interface{}); ok {
			return s
		}
	}
	return nil
}

// StringSlice returns the value at path as a []string, converting each element
// with the same rules as String. It returns nil when the path is absent or does
// not hold a slice.
func (m *Map) StringSlice(path string) []string {
	if v, ok := m.Get(path); ok {
		if s, ok := v.([]interface{}); ok {
			out := make([]string, 0, len(s))
			for _, item := range s {
				str, ok := toString(item)
				if !ok {
					return nil
				}
				out = append(out, str)
			}
			return out
		}
	}
	return nil
}

// IsNil reports whether the path exists and holds an untyped nil.
func (m *Map) IsNil(path string) bool {
	v, ok := m.Get(path)
	return ok && v == nil
}

// FromJSON decodes a JSON object into a Map. It fails if the document is not a
// JSON object.
func FromJSON(data []byte) (*Map, error) {
	var raw map[string]interface{}
	if err := json.Unmarshal(data, &raw); err != nil {
		return nil, fmt.Errorf("mapq: decode json: %w", err)
	}
	return New(raw), nil
}

// JSON encodes the Map as JSON.
func (m *Map) JSON() ([]byte, error) { return json.Marshal(m.data) }

// MarshalJSON implements json.Marshaler.
func (m *Map) MarshalJSON() ([]byte, error) { return json.Marshal(m.data) }

// UnmarshalJSON implements json.Unmarshaler, replacing the Map contents.
func (m *Map) UnmarshalJSON(data []byte) error {
	var raw map[string]interface{}
	if err := json.Unmarshal(data, &raw); err != nil {
		return err
	}
	m.data = raw
	return nil
}

func toString(v interface{}) (string, bool) {
	switch s := v.(type) {
	case string:
		return s, true
	case []byte:
		return string(s), true
	case bool:
		return strconv.FormatBool(s), true
	case float64:
		return strconv.FormatFloat(s, 'f', -1, 64), true
	case float32:
		return strconv.FormatFloat(float64(s), 'f', -1, 32), true
	case int:
		return strconv.Itoa(s), true
	case int8:
		return strconv.FormatInt(int64(s), 10), true
	case int16:
		return strconv.FormatInt(int64(s), 10), true
	case int32:
		return strconv.FormatInt(int64(s), 10), true
	case int64:
		return strconv.FormatInt(s, 10), true
	case uint:
		return strconv.FormatUint(uint64(s), 10), true
	case uint8:
		return strconv.FormatUint(uint64(s), 10), true
	case uint16:
		return strconv.FormatUint(uint64(s), 10), true
	case uint32:
		return strconv.FormatUint(uint64(s), 10), true
	case uint64:
		return strconv.FormatUint(s, 10), true
	default:
		return "", false
	}
}

func toBool(v interface{}) (bool, bool) {
	switch b := v.(type) {
	case bool:
		return b, true
	case string:
		parsed, err := strconv.ParseBool(b)
		return parsed, err == nil
	default:
		if n, ok := toFloat64(v); ok {
			return n != 0, true
		}
		return false, false
	}
}

func toInt64(v interface{}) (int64, bool) {
	switch n := v.(type) {
	case int:
		return int64(n), true
	case int8:
		return int64(n), true
	case int16:
		return int64(n), true
	case int32:
		return int64(n), true
	case int64:
		return n, true
	case uint:
		return int64(n), true
	case uint8:
		return int64(n), true
	case uint16:
		return int64(n), true
	case uint32:
		return int64(n), true
	case uint64:
		if n > 1<<63-1 {
			return 0, false
		}
		return int64(n), true
	case float32:
		return int64(n), true
	case float64:
		return int64(n), true
	case json.Number:
		if i, err := n.Int64(); err == nil {
			return i, true
		}
		if f, err := n.Float64(); err == nil {
			return int64(f), true
		}
		return 0, false
	case string:
		if i, err := strconv.ParseInt(n, 10, 64); err == nil {
			return i, true
		}
		if f, err := strconv.ParseFloat(n, 64); err == nil {
			return int64(f), true
		}
		return 0, false
	default:
		return 0, false
	}
}

func toFloat64(v interface{}) (float64, bool) {
	switch n := v.(type) {
	case int:
		return float64(n), true
	case int8:
		return float64(n), true
	case int16:
		return float64(n), true
	case int32:
		return float64(n), true
	case int64:
		return float64(n), true
	case uint:
		return float64(n), true
	case uint8:
		return float64(n), true
	case uint16:
		return float64(n), true
	case uint32:
		return float64(n), true
	case uint64:
		return float64(n), true
	case float32:
		return float64(n), true
	case float64:
		return n, true
	case json.Number:
		f, err := n.Float64()
		return f, err == nil
	case string:
		f, err := strconv.ParseFloat(n, 64)
		return f, err == nil
	default:
		return 0, false
	}
}

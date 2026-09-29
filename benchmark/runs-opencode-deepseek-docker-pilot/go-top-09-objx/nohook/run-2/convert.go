package dynmap

import (
	"encoding/json"
	"reflect"
)

// asString reports whether v is a string.
func asString(v interface{}) (string, bool) {
	s, ok := v.(string)
	return s, ok
}

// asBool reports whether v is a bool.
func asBool(v interface{}) (bool, bool) {
	b, ok := v.(bool)
	return b, ok
}

// asInt64 converts any signed, unsigned or floating point number to
// int64. Floating point values are truncated.
func asInt64(v interface{}) (int64, bool) {
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
		return int64(n), true
	case float32:
		return int64(n), true
	case float64:
		return int64(n), true
	case json.Number:
		i, err := n.Int64()
		return i, err == nil
	default:
		return 0, false
	}
}

// asFloat64 converts any signed, unsigned or floating point number to
// float64.
func asFloat64(v interface{}) (float64, bool) {
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
	default:
		return 0, false
	}
}

// asSlice converts v to []interface{}. Slices and arrays of any element
// type are accepted via reflection.
func asSlice(v interface{}) ([]interface{}, bool) {
	if s, ok := v.([]interface{}); ok {
		return s, true
	}
	rv := reflect.ValueOf(v)
	if !rv.IsValid() || (rv.Kind() != reflect.Slice && rv.Kind() != reflect.Array) {
		return nil, false
	}
	out := make([]interface{}, rv.Len())
	for i := 0; i < rv.Len(); i++ {
		out[i] = rv.Index(i).Interface()
	}
	return out, true
}

// indexInto returns element i of a slice or array value.
func indexInto(v interface{}, i int) (interface{}, bool) {
	if i < 0 {
		return nil, false
	}
	if s, ok := v.([]interface{}); ok {
		if i < len(s) {
			return s[i], true
		}
		return nil, false
	}
	rv := reflect.ValueOf(v)
	if !rv.IsValid() || (rv.Kind() != reflect.Slice && rv.Kind() != reflect.Array) {
		return nil, false
	}
	if i < rv.Len() {
		return rv.Index(i).Interface(), true
	}
	return nil, false
}

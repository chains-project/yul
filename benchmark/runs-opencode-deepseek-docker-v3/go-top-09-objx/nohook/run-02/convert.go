package fluentmap

import (
	"encoding/json"
	"fmt"
	"reflect"
	"strconv"
	"strings"
)

// toInt converts v to an int when a safe, lossless conversion exists.
func toInt(v interface{}) (int, bool) {
	n, ok := toInt64(v)
	if !ok {
		return 0, false
	}
	return int(n), true
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
		if n > uint64(^uint64(0)>>1) {
			return 0, false
		}
		return int64(n), true
	case float32:
		return floatToInt64(float64(n))
	case float64:
		return floatToInt64(n)
	case json.Number:
		if i, err := n.Int64(); err == nil {
			return i, true
		}
		if f, err := n.Float64(); err == nil {
			return floatToInt64(f)
		}
		return 0, false
	case string:
		s := strings.TrimSpace(n)
		if i, err := strconv.ParseInt(s, 10, 64); err == nil {
			return i, true
		}
		if f, err := strconv.ParseFloat(s, 64); err == nil {
			return floatToInt64(f)
		}
		return 0, false
	default:
		return 0, false
	}
}

func floatToInt64(f float64) (int64, bool) {
	if f != float64(int64(f)) {
		return 0, false
	}
	return int64(f), true
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
		f, err := strconv.ParseFloat(strings.TrimSpace(n), 64)
		return f, err == nil
	default:
		return 0, false
	}
}

func toString(v interface{}) (string, bool) {
	switch n := v.(type) {
	case string:
		return n, true
	case []byte:
		return string(n), true
	case json.Number:
		return n.String(), true
	case fmt.Stringer:
		return n.String(), true
	default:
		return "", false
	}
}

func toBool(v interface{}) (bool, bool) {
	switch n := v.(type) {
	case bool:
		return n, true
	case string:
		b, err := strconv.ParseBool(strings.TrimSpace(n))
		return b, err == nil
	case json.Number:
		f, err := n.Float64()
		if err != nil {
			return false, false
		}
		return f != 0, true
	default:
		if f, ok := toFloat64(v); ok {
			return f != 0, true
		}
		return false, false
	}
}

func toSlice(v interface{}) ([]interface{}, bool) {
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

func toMap(v interface{}) (map[string]interface{}, bool) {
	switch t := v.(type) {
	case map[string]interface{}:
		return t, true
	case *Map:
		if t == nil {
			return nil, false
		}
		return t.data, true
	default:
		return nil, false
	}
}

func toStrings(v interface{}) ([]string, bool) {
	slice, ok := toSlice(v)
	if !ok {
		return nil, false
	}
	out := make([]string, 0, len(slice))
	for _, item := range slice {
		s, ok := toString(item)
		if !ok {
			return nil, false
		}
		out = append(out, s)
	}
	return out, true
}

package mapfluent

import (
	"encoding/json"
	"fmt"
	"math"
	"reflect"
	"strconv"
	"strings"
)

// String returns the wrapped value as a string. Objects, arrays and other
// non-string values are formatted with fmt, and nil yields "".
func (m *Map) String() string {
	switch v := m.Value().(type) {
	case nil:
		return ""
	case string:
		return v
	case []byte:
		return string(v)
	case error:
		return v.Error()
	case fmt.Stringer:
		return v.String()
	default:
		return fmt.Sprintf("%v", v)
	}
}

// StringOr returns the value as a string, or def when it is nil.
func (m *Map) StringOr(def string) string {
	if m.IsNil() {
		return def
	}
	return m.String()
}

// StringSlice returns the value as a slice of strings. Scalars are returned as
// a single-element slice and non-array values yield nil.
func (m *Map) StringSlice() []string {
	switch v := m.Value().(type) {
	case []interface{}:
		out := make([]string, len(v))
		for i, item := range v {
			out[i] = Wrap(item).String()
		}
		return out
	case []string:
		return v
	case nil:
		return nil
	default:
		return []string{m.String()}
	}
}

// Int returns the value as an int, truncating floats and returning 0 when the
// value cannot be converted.
func (m *Map) Int() int {
	n, _ := asInt64(m.Value())
	return int(n)
}

// IntOr returns the value as an int, or def when it cannot be converted.
func (m *Map) IntOr(def int) int {
	n, ok := asInt64(m.Value())
	if !ok {
		return def
	}
	return int(n)
}

// Int64 returns the value as an int64, returning 0 when the value cannot be
// converted.
func (m *Map) Int64() int64 {
	n, _ := asInt64(m.Value())
	return n
}

// Float64 returns the value as a float64, returning 0 when the value cannot be
// converted.
func (m *Map) Float64() float64 {
	f, _ := asFloat64(m.Value())
	return f
}

// Float64Or returns the value as a float64, or def when it cannot be
// converted.
func (m *Map) Float64Or(def float64) float64 {
	f, ok := asFloat64(m.Value())
	if !ok {
		return def
	}
	return f
}

// Bool returns the value as a bool, returning false when the value cannot be
// converted.
func (m *Map) Bool() bool {
	b, _ := asBool(m.Value())
	return b
}

// BoolOr returns the value as a bool, or def when it cannot be converted.
func (m *Map) BoolOr(def bool) bool {
	b, ok := asBool(m.Value())
	if !ok {
		return def
	}
	return b
}

func asInt64(value interface{}) (int64, bool) {
	switch v := value.(type) {
	case nil:
		return 0, false
	case bool:
		if v {
			return 1, true
		}
		return 0, true
	case string:
		n, err := strconv.ParseInt(strings.TrimSpace(v), 10, 64)
		if err != nil {
			if f, ferr := strconv.ParseFloat(strings.TrimSpace(v), 64); ferr == nil {
				return int64(f), true
			}
			return 0, false
		}
		return n, true
	case json.Number:
		if n, err := v.Int64(); err == nil {
			return n, true
		}
		f, err := v.Float64()
		if err != nil {
			return 0, false
		}
		return int64(f), true
	}
	return numericInt64(reflect.ValueOf(value))
}

func asFloat64(value interface{}) (float64, bool) {
	switch v := value.(type) {
	case nil:
		return 0, false
	case bool:
		if v {
			return 1, true
		}
		return 0, true
	case string:
		f, err := strconv.ParseFloat(strings.TrimSpace(v), 64)
		if err != nil {
			return 0, false
		}
		return f, true
	case json.Number:
		f, err := v.Float64()
		if err != nil {
			return 0, false
		}
		return f, true
	}
	return numericFloat64(reflect.ValueOf(value))
}

func asBool(value interface{}) (bool, bool) {
	switch v := value.(type) {
	case nil:
		return false, false
	case bool:
		return v, true
	case string:
		b, err := strconv.ParseBool(strings.TrimSpace(v))
		if err != nil {
			return false, false
		}
		return b, true
	}
	if n, ok := asFloat64(value); ok {
		return n != 0, true
	}
	return false, false
}

func numericInt64(rv reflect.Value) (int64, bool) {
	switch rv.Kind() {
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return rv.Int(), true
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		if rv.Uint() > math.MaxInt64 {
			return math.MaxInt64, true
		}
		return int64(rv.Uint()), true
	case reflect.Float32, reflect.Float64:
		return int64(rv.Float()), true
	default:
		return 0, false
	}
}

func numericFloat64(rv reflect.Value) (float64, bool) {
	switch rv.Kind() {
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return float64(rv.Int()), true
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		return float64(rv.Uint()), true
	case reflect.Float32, reflect.Float64:
		return rv.Float(), true
	default:
		return 0, false
	}
}

package chainmap

import (
	"encoding/json"
	"fmt"
	"math"
	"strconv"
	"strings"
)

// Value is a fluent wrapper around an arbitrary interface{} value pulled
// from a Map or Slice. Like Map, it records the first error encountered and
// exposes it through Err.
type Value struct {
	val interface{}
	err error
}

func newValue(val interface{}) *Value { return &Value{val: val} }

func errValue(err error) *Value { return &Value{err: err} }

// Err returns the first error recorded while producing or reading the value.
func (v *Value) Err() error {
	if v == nil {
		return nil
	}
	return v.err
}

// Interface returns the underlying value.
func (v *Value) Interface() interface{} {
	if v == nil {
		return nil
	}
	return v.val
}

// Raw is an alias for Interface.
func (v *Value) Raw() interface{} { return v.Interface() }

// Exists reports whether the value was found without error.
func (v *Value) Exists() bool { return v != nil && v.err == nil }

// IsNil reports whether the value exists and is nil.
func (v *Value) IsNil() bool { return v.Exists() && v.val == nil }

// String returns the underlying string. It records ErrTypeMismatch if the
// value is not a string. Missing values yield the empty string.
func (v *Value) String() string {
	if v == nil || v.err != nil {
		return ""
	}
	switch x := v.val.(type) {
	case string:
		return x
	case nil:
		return ""
	default:
		v.err = fmt.Errorf("%w: expected string, got %T", ErrTypeMismatch, v.val)
		return ""
	}
}

// StringOr returns the underlying string or def when the value is missing
// or not a string. It never records an error.
func (v *Value) StringOr(def string) string {
	if v == nil || v.err != nil {
		return def
	}
	if s, ok := v.val.(string); ok {
		return s
	}
	return def
}

// Int returns the underlying value as an int. Numeric strings and JSON
// numbers are accepted. It records ErrTypeMismatch on failure.
func (v *Value) Int() int { return int(v.Int64()) }

// IntOr returns the underlying value as an int or def on failure.
func (v *Value) IntOr(def int) int {
	if v == nil || v.err != nil {
		return def
	}
	n, ok := toInt64(v.val)
	if !ok || n > math.MaxInt || n < math.MinInt {
		return def
	}
	return int(n)
}

// Int64 returns the underlying value as an int64. Numeric strings and JSON
// numbers are accepted. It records ErrTypeMismatch on failure.
func (v *Value) Int64() int64 {
	if v == nil || v.err != nil {
		return 0
	}
	n, ok := toInt64(v.val)
	if !ok {
		v.err = fmt.Errorf("%w: expected integer, got %T", ErrTypeMismatch, v.val)
		return 0
	}
	return n
}

// Int64Or returns the underlying value as an int64 or def on failure.
func (v *Value) Int64Or(def int64) int64 {
	if v == nil || v.err != nil {
		return def
	}
	n, ok := toInt64(v.val)
	if !ok {
		return def
	}
	return n
}

// Float64 returns the underlying value as a float64. Numeric strings and
// JSON numbers are accepted. It records ErrTypeMismatch on failure.
func (v *Value) Float64() float64 {
	if v == nil || v.err != nil {
		return 0
	}
	f, ok := toFloat64(v.val)
	if !ok {
		v.err = fmt.Errorf("%w: expected number, got %T", ErrTypeMismatch, v.val)
		return 0
	}
	return f
}

// Float64Or returns the underlying value as a float64 or def on failure.
func (v *Value) Float64Or(def float64) float64 {
	if v == nil || v.err != nil {
		return def
	}
	f, ok := toFloat64(v.val)
	if !ok {
		return def
	}
	return f
}

// Bool returns the underlying bool. Strings are parsed with
// strconv.ParseBool. It records ErrTypeMismatch on failure.
func (v *Value) Bool() bool {
	if v == nil || v.err != nil {
		return false
	}
	b, ok := toBool(v.val)
	if !ok {
		v.err = fmt.Errorf("%w: expected bool, got %T", ErrTypeMismatch, v.val)
		return false
	}
	return b
}

// BoolOr returns the underlying bool or def on failure.
func (v *Value) BoolOr(def bool) bool {
	if v == nil || v.err != nil {
		return def
	}
	b, ok := toBool(v.val)
	if !ok {
		return def
	}
	return b
}

// Get returns the value stored under key when the receiver wraps a map. It
// records ErrTypeMismatch for non-map values and ErrNotFound for missing
// keys.
func (v *Value) Get(key string) *Value {
	if v == nil {
		return errValue(fmt.Errorf("%w: %q", ErrNotFound, key))
	}
	if v.err != nil {
		return errValue(v.err)
	}
	m, ok := v.val.(map[string]interface{})
	if !ok {
		return errValue(fmt.Errorf("%w: expected map, got %T", ErrTypeMismatch, v.val))
	}
	val, ok := m[key]
	if !ok {
		return errValue(fmt.Errorf("%w: %q", ErrNotFound, key))
	}
	return newValue(val)
}

// Index returns the element at i when the receiver wraps a slice. It records
// ErrTypeMismatch for non-slices and ErrIndexOutOfRange for invalid indexes.
func (v *Value) Index(i int) *Value {
	if v == nil {
		return errValue(fmt.Errorf("%w: %d", ErrIndexOutOfRange, i))
	}
	if v.err != nil {
		return errValue(v.err)
	}
	s, ok := v.val.([]interface{})
	if !ok {
		return errValue(fmt.Errorf("%w: expected slice, got %T", ErrTypeMismatch, v.val))
	}
	if i < 0 || i >= len(s) {
		return errValue(fmt.Errorf("%w: %d", ErrIndexOutOfRange, i))
	}
	return newValue(s[i])
}

// Path resolves a dot-separated path against the value. Segments descend
// through maps by key and through slices by numeric index:
//
//	user.roles.0        // data["user"]["roles"][0]
//
// It records ErrNotFound, ErrIndexOutOfRange, or ErrTypeMismatch on failure.
func (v *Value) Path(path string) *Value {
	if v == nil {
		return errValue(fmt.Errorf("%w: %q", ErrNotFound, path))
	}
	cur := v
	for _, part := range splitPath(path) {
		if cur.err != nil {
			return cur
		}
		if _, ok := cur.val.([]interface{}); ok {
			i, err := strconv.Atoi(part)
			if err != nil {
				return errValue(fmt.Errorf("%w: expected slice index, got %q", ErrTypeMismatch, part))
			}
			cur = cur.Index(i)
			continue
		}
		cur = cur.Get(part)
	}
	return cur
}

// Map returns the receiver as a *Map. It records ErrTypeMismatch when the
// value is not a map.
func (v *Value) Map() *Map {
	if v == nil {
		return &Map{err: fmt.Errorf("%w: expected map, got <nil>", ErrTypeMismatch)}
	}
	if v.err != nil {
		return &Map{err: v.err}
	}
	m, ok := v.val.(map[string]interface{})
	if !ok {
		return &Map{err: fmt.Errorf("%w: expected map, got %T", ErrTypeMismatch, v.val)}
	}
	return &Map{data: m}
}

// Slice returns the receiver as a *Slice. It records ErrTypeMismatch when
// the value is not a slice.
func (v *Value) Slice() *Slice {
	if v == nil {
		return &Slice{err: fmt.Errorf("%w: expected slice, got <nil>", ErrTypeMismatch)}
	}
	if v.err != nil {
		return &Slice{err: v.err}
	}
	s, ok := v.val.([]interface{})
	if !ok {
		return &Slice{err: fmt.Errorf("%w: expected slice, got %T", ErrTypeMismatch, v.val)}
	}
	return &Slice{data: s}
}

func toInt64(val interface{}) (int64, bool) {
	switch x := val.(type) {
	case int:
		return int64(x), true
	case int8:
		return int64(x), true
	case int16:
		return int64(x), true
	case int32:
		return int64(x), true
	case int64:
		return x, true
	case uint:
		if uint64(x) > math.MaxInt64 {
			return 0, false
		}
		return int64(x), true
	case uint8:
		return int64(x), true
	case uint16:
		return int64(x), true
	case uint32:
		return int64(x), true
	case uint64:
		if x > math.MaxInt64 {
			return 0, false
		}
		return int64(x), true
	case float32:
		return floatToInt64(float64(x))
	case float64:
		return floatToInt64(x)
	case json.Number:
		n, err := x.Int64()
		return n, err == nil
	case string:
		n, err := strconv.ParseInt(strings.TrimSpace(x), 10, 64)
		return n, err == nil
	default:
		return 0, false
	}
}

func floatToInt64(f float64) (int64, bool) {
	if math.IsNaN(f) || math.IsInf(f, 0) || f != math.Trunc(f) {
		return 0, false
	}
	if f > math.MaxInt64 || f < math.MinInt64 {
		return 0, false
	}
	return int64(f), true
}

func toFloat64(val interface{}) (float64, bool) {
	switch x := val.(type) {
	case int:
		return float64(x), true
	case int8:
		return float64(x), true
	case int16:
		return float64(x), true
	case int32:
		return float64(x), true
	case int64:
		return float64(x), true
	case uint:
		return float64(x), true
	case uint8:
		return float64(x), true
	case uint16:
		return float64(x), true
	case uint32:
		return float64(x), true
	case uint64:
		return float64(x), true
	case float32:
		return float64(x), true
	case float64:
		return x, true
	case json.Number:
		f, err := x.Float64()
		return f, err == nil
	case string:
		f, err := strconv.ParseFloat(strings.TrimSpace(x), 64)
		return f, err == nil
	default:
		return 0, false
	}
}

func toBool(val interface{}) (bool, bool) {
	switch x := val.(type) {
	case bool:
		return x, true
	case string:
		b, err := strconv.ParseBool(strings.TrimSpace(x))
		return b, err == nil
	default:
		return false, false
	}
}

func unwrap(value interface{}) interface{} {
	switch x := value.(type) {
	case nil:
		return nil
	case *Map:
		if x == nil {
			return nil
		}
		return x.data
	case *Slice:
		if x == nil {
			return nil
		}
		return x.data
	case *Value:
		if x == nil {
			return nil
		}
		return x.val
	default:
		return value
	}
}

func deepCopy(value interface{}) interface{} {
	switch x := value.(type) {
	case map[string]interface{}:
		out := make(map[string]interface{}, len(x))
		for k, v := range x {
			out[k] = deepCopy(v)
		}
		return out
	case []interface{}:
		out := make([]interface{}, len(x))
		for i, v := range x {
			out[i] = deepCopy(v)
		}
		return out
	default:
		return value
	}
}

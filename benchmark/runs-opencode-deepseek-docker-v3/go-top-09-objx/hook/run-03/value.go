package mapx

import (
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
)

// Value is a resolved value paired with any lookup or conversion error.
// Accessor methods return the zero value on error and record it in Err.
type Value struct {
	raw interface{}
	err error
}

// Raw returns the underlying value.
func (v *Value) Raw() interface{} { return v.raw }

// Interface returns the underlying value. It is an alias for Raw.
func (v *Value) Interface() interface{} { return v.raw }

// Err returns the lookup or conversion error, if any.
func (v *Value) Err() error { return v.err }

// Exists reports whether a value was resolved without error.
func (v *Value) Exists() bool { return v != nil && v.err == nil }

// IsNil reports whether the resolved value is nil.
func (v *Value) IsNil() bool { return v.raw == nil }

// Get navigates deeper into the current value, which must be a map or slice.
func (v *Value) Get(path string) *Value {
	if v.err != nil {
		return v
	}
	out, err := walk(v.raw, path)
	return &Value{raw: out, err: err}
}

// String returns the value as a string.
func (v *Value) String() string {
	if v.err != nil || v.raw == nil {
		return ""
	}
	switch s := v.raw.(type) {
	case string:
		return s
	case []byte:
		return string(s)
	default:
		return fmt.Sprint(v.raw)
	}
}

// Int returns the value as an int.
func (v *Value) Int() int {
	n, err := v.int64()
	if err != nil {
		v.fail(err)
		return 0
	}
	return int(n)
}

// Int64 returns the value as an int64.
func (v *Value) Int64() int64 {
	n, err := v.int64()
	if err != nil {
		v.fail(err)
		return 0
	}
	return n
}

// Float64 returns the value as a float64.
func (v *Value) Float64() float64 {
	f, err := v.float64()
	if err != nil {
		v.fail(err)
		return 0
	}
	return f
}

// Bool returns the value as a bool.
func (v *Value) Bool() bool {
	if v.err != nil {
		return false
	}
	switch b := v.raw.(type) {
	case bool:
		return b
	case string:
		parsed, err := strconv.ParseBool(strings.TrimSpace(b))
		if err != nil {
			v.fail(fmt.Errorf("%w: cannot convert %q to bool", ErrTypeMismatch, b))
			return false
		}
		return parsed
	case int:
		return b != 0
	case int64:
		return b != 0
	case float64:
		return b != 0
	default:
		v.fail(fmt.Errorf("%w: cannot convert %T to bool", ErrTypeMismatch, v.raw))
		return false
	}
}

// Map returns the value as a map[string]interface{}.
func (v *Value) Map() map[string]interface{} {
	if v.err != nil {
		return nil
	}
	switch m := v.raw.(type) {
	case map[string]interface{}:
		return m
	case Map:
		return map[string]interface{}(m)
	default:
		v.fail(fmt.Errorf("%w: cannot convert %T to map", ErrTypeMismatch, v.raw))
		return nil
	}
}

// Slice returns the value as a []interface{}.
func (v *Value) Slice() []interface{} {
	if v.err != nil {
		return nil
	}
	if s, ok := asSlice(v.raw); ok {
		return s
	}
	v.fail(fmt.Errorf("%w: cannot convert %T to slice", ErrTypeMismatch, v.raw))
	return nil
}

// Or returns the current value if valid, otherwise fallback.
func (v *Value) Or(fallback interface{}) *Value {
	if v.err != nil || v.raw == nil {
		return &Value{raw: fallback}
	}
	return v
}

func (v *Value) fail(err error) {
	if v.err == nil {
		v.err = err
	}
}

func (v *Value) int64() (int64, error) {
	if v.err != nil {
		return 0, v.err
	}
	if v.raw == nil {
		return 0, fmt.Errorf("%w: nil value", ErrTypeMismatch)
	}
	switch n := v.raw.(type) {
	case int:
		return int64(n), nil
	case int8:
		return int64(n), nil
	case int16:
		return int64(n), nil
	case int32:
		return int64(n), nil
	case int64:
		return n, nil
	case uint:
		return int64(n), nil
	case uint8:
		return int64(n), nil
	case uint16:
		return int64(n), nil
	case uint32:
		return int64(n), nil
	case uint64:
		return int64(n), nil
	case float32:
		return int64(n), nil
	case float64:
		return int64(n), nil
	case json.Number:
		return n.Int64()
	case string:
		s := strings.TrimSpace(n)
		if i, err := strconv.ParseInt(s, 10, 64); err == nil {
			return i, nil
		}
		if f, err := strconv.ParseFloat(s, 64); err == nil {
			return int64(f), nil
		}
	}
	return 0, fmt.Errorf("%w: cannot convert %T to int64", ErrTypeMismatch, v.raw)
}

func (v *Value) float64() (float64, error) {
	if v.err != nil {
		return 0, v.err
	}
	if v.raw == nil {
		return 0, fmt.Errorf("%w: nil value", ErrTypeMismatch)
	}
	switch n := v.raw.(type) {
	case float64:
		return n, nil
	case float32:
		return float64(n), nil
	case int:
		return float64(n), nil
	case int64:
		return float64(n), nil
	case json.Number:
		return n.Float64()
	case string:
		f, err := strconv.ParseFloat(strings.TrimSpace(n), 64)
		if err == nil {
			return f, nil
		}
	}
	if i, err := v.int64(); err == nil {
		return float64(i), nil
	}
	return 0, fmt.Errorf("%w: cannot convert %T to float64", ErrTypeMismatch, v.raw)
}

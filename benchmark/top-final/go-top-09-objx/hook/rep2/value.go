package objx

import "fmt"

// Value wraps the result of a Map lookup, giving convenient, panic-free
// access to its underlying data as a specific type.
type Value struct {
	data interface{}
}

// Data returns the raw underlying value.
func (v *Value) Data() interface{} {
	if v == nil {
		return nil
	}
	return v.data
}

// IsNil reports whether the value is absent or nil.
func (v *Value) IsNil() bool {
	return v == nil || v.data == nil
}

// Get continues the chain, resolving selector against this value if it
// holds a map.
func (v *Value) Get(selector string) *Value {
	if v.IsNil() {
		return &Value{}
	}
	switch d := v.data.(type) {
	case Map:
		return d.Get(selector)
	case map[string]interface{}:
		return Map(d).Get(selector)
	default:
		return &Value{}
	}
}

// Str returns the value as a string, or defaultValue[0] (or "" if not
// given) if the value isn't a string.
func (v *Value) Str(defaultValue ...string) string {
	if s, ok := v.Data().(string); ok {
		return s
	}
	if len(defaultValue) > 0 {
		return defaultValue[0]
	}
	return ""
}

// IsStr reports whether the value is a string.
func (v *Value) IsStr() bool {
	_, ok := v.Data().(string)
	return ok
}

// MustStr returns the value as a string, panicking if it isn't one.
func (v *Value) MustStr() string {
	s, ok := v.Data().(string)
	if !ok {
		panic(fmt.Sprintf("objx: value %#v is not a string", v.Data()))
	}
	return s
}

// Bool returns the value as a bool, or defaultValue[0] (or false if not
// given) if the value isn't a bool.
func (v *Value) Bool(defaultValue ...bool) bool {
	if b, ok := v.Data().(bool); ok {
		return b
	}
	if len(defaultValue) > 0 {
		return defaultValue[0]
	}
	return false
}

// IsBool reports whether the value is a bool.
func (v *Value) IsBool() bool {
	_, ok := v.Data().(bool)
	return ok
}

// toFloat64 converts any numeric kind (as produced by encoding/json or set
// directly) to a float64.
func toFloat64(data interface{}) (float64, bool) {
	switch n := data.(type) {
	case float64:
		return n, true
	case float32:
		return float64(n), true
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
	default:
		return 0, false
	}
}

// Float64 returns the value as a float64, or defaultValue[0] (or 0 if not
// given) if the value isn't numeric.
func (v *Value) Float64(defaultValue ...float64) float64 {
	if f, ok := toFloat64(v.Data()); ok {
		return f
	}
	if len(defaultValue) > 0 {
		return defaultValue[0]
	}
	return 0
}

// Int returns the value as an int, or defaultValue[0] (or 0 if not given)
// if the value isn't numeric.
func (v *Value) Int(defaultValue ...int) int {
	if f, ok := toFloat64(v.Data()); ok {
		return int(f)
	}
	if len(defaultValue) > 0 {
		return defaultValue[0]
	}
	return 0
}

// Int64 returns the value as an int64, or defaultValue[0] (or 0 if not
// given) if the value isn't numeric.
func (v *Value) Int64(defaultValue ...int64) int64 {
	if f, ok := toFloat64(v.Data()); ok {
		return int64(f)
	}
	if len(defaultValue) > 0 {
		return defaultValue[0]
	}
	return 0
}

// IsNumeric reports whether the value is any numeric kind.
func (v *Value) IsNumeric() bool {
	_, ok := toFloat64(v.Data())
	return ok
}

// Map returns the value as a Map, or an empty Map if it isn't one.
func (v *Value) Map() Map {
	switch m := v.Data().(type) {
	case Map:
		return m
	case map[string]interface{}:
		return Map(m)
	default:
		return Map{}
	}
}

// IsMap reports whether the value is a map.
func (v *Value) IsMap() bool {
	switch v.Data().(type) {
	case Map, map[string]interface{}:
		return true
	default:
		return false
	}
}

// Slice returns the value as a []interface{}, or nil if it isn't a slice.
func (v *Value) Slice() []interface{} {
	s, _ := v.Data().([]interface{})
	return s
}

// IsSlice reports whether the value is a []interface{}.
func (v *Value) IsSlice() bool {
	_, ok := v.Data().([]interface{})
	return ok
}

// StrSlice returns the value as a []string, skipping any elements that
// aren't strings. It returns nil if the value isn't a slice.
func (v *Value) StrSlice() []string {
	s := v.Slice()
	if s == nil {
		return nil
	}
	out := make([]string, 0, len(s))
	for _, item := range s {
		if str, ok := item.(string); ok {
			out = append(out, str)
		}
	}
	return out
}

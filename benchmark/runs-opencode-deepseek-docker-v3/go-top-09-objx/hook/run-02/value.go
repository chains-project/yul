package mapx

import (
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
)

type Value struct {
	raw    interface{}
	exists bool
}

func newValue(raw interface{}, exists bool) *Value {
	return &Value{raw: raw, exists: exists}
}

func (v *Value) Interface() interface{} {
	if v == nil {
		return nil
	}
	return v.raw
}

func (v *Value) Raw() (interface{}, bool) {
	if v == nil {
		return nil, false
	}
	return v.raw, v.exists
}

func (v *Value) Exists() bool {
	return v != nil && v.exists
}

func (v *Value) IsNil() bool {
	return v == nil || v.raw == nil
}

func (v *Value) String() string {
	if v == nil || v.raw == nil {
		return ""
	}
	switch t := v.raw.(type) {
	case string:
		return t
	case []byte:
		return string(t)
	case bool:
		return strconv.FormatBool(t)
	case float64:
		return strconv.FormatFloat(t, 'f', -1, 64)
	case float32:
		return strconv.FormatFloat(float64(t), 'f', -1, 32)
	case int:
		return strconv.Itoa(t)
	case int64:
		return strconv.FormatInt(t, 10)
	case int32:
		return strconv.FormatInt(int64(t), 10)
	case uint64:
		return strconv.FormatUint(t, 10)
	case fmt.Stringer:
		return t.String()
	default:
		return fmt.Sprintf("%v", t)
	}
}

func (v *Value) StringOr(def string) string {
	if !v.Exists() {
		return def
	}
	return v.String()
}

func (v *Value) Int() int {
	n, _ := toInt64(v.Interface())
	return int(n)
}

func (v *Value) Int64() int64 {
	n, _ := toInt64(v.Interface())
	return n
}

func (v *Value) IntOr(def int) int {
	if !v.Exists() {
		return def
	}
	n, ok := toInt64(v.raw)
	if !ok {
		return def
	}
	return int(n)
}

func (v *Value) Float() float64 {
	f, _ := toFloat64(v.Interface())
	return f
}

func (v *Value) FloatOr(def float64) float64 {
	if !v.Exists() {
		return def
	}
	f, ok := toFloat64(v.raw)
	if !ok {
		return def
	}
	return f
}

func (v *Value) Bool() bool {
	b, _ := toBool(v.Interface())
	return b
}

func (v *Value) BoolOr(def bool) bool {
	if !v.Exists() {
		return def
	}
	b, ok := toBool(v.raw)
	if !ok {
		return def
	}
	return b
}

func (v *Value) Slice() []interface{} {
	arr, _ := asSlice(v.Interface())
	return arr
}

func (v *Value) Strings() []string {
	arr := v.Slice()
	if arr == nil {
		return nil
	}
	out := make([]string, len(arr))
	for i, item := range arr {
		out[i] = newValue(item, true).String()
	}
	return out
}

func (v *Value) Map() *Map {
	m, _ := asMap(v.Interface())
	return New(m)
}

func toInt64(raw interface{}) (int64, bool) {
	switch t := raw.(type) {
	case int:
		return int64(t), true
	case int8:
		return int64(t), true
	case int16:
		return int64(t), true
	case int32:
		return int64(t), true
	case int64:
		return t, true
	case uint:
		return int64(t), true
	case uint8:
		return int64(t), true
	case uint16:
		return int64(t), true
	case uint32:
		return int64(t), true
	case uint64:
		return int64(t), true
	case float32:
		return int64(t), true
	case float64:
		return int64(t), true
	case bool:
		if t {
			return 1, true
		}
		return 0, true
	case json.Number:
		if n, err := t.Int64(); err == nil {
			return n, true
		}
		if f, err := t.Float64(); err == nil {
			return int64(f), true
		}
		return 0, false
	case string:
		s := strings.TrimSpace(t)
		if n, err := strconv.ParseInt(s, 10, 64); err == nil {
			return n, true
		}
		if f, err := strconv.ParseFloat(s, 64); err == nil {
			return int64(f), true
		}
		return 0, false
	default:
		return 0, false
	}
}

func toFloat64(raw interface{}) (float64, bool) {
	switch t := raw.(type) {
	case float64:
		return t, true
	case float32:
		return float64(t), true
	case int:
		return float64(t), true
	case int8:
		return float64(t), true
	case int16:
		return float64(t), true
	case int32:
		return float64(t), true
	case int64:
		return float64(t), true
	case uint:
		return float64(t), true
	case uint8:
		return float64(t), true
	case uint16:
		return float64(t), true
	case uint32:
		return float64(t), true
	case uint64:
		return float64(t), true
	case json.Number:
		f, err := t.Float64()
		return f, err == nil
	case string:
		f, err := strconv.ParseFloat(strings.TrimSpace(t), 64)
		return f, err == nil
	default:
		return 0, false
	}
}

func toBool(raw interface{}) (bool, bool) {
	switch t := raw.(type) {
	case bool:
		return t, true
	case json.Number:
		f, err := t.Float64()
		if err != nil {
			return false, false
		}
		return f != 0, true
	case string:
		s := strings.TrimSpace(t)
		if b, err := strconv.ParseBool(s); err == nil {
			return b, true
		}
		switch strings.ToLower(s) {
		case "yes":
			return true, true
		case "no":
			return false, true
		}
		return false, false
	}
	if f, ok := toFloat64(raw); ok {
		return f != 0, true
	}
	return false, false
}

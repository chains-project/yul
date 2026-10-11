package mapfluent

import (
	"fmt"
	"math"
	"reflect"
	"strconv"
	"strings"
)

func lookup(node any, segs []segment) (any, bool) {
	cur := node
	for _, seg := range segs {
		switch n := cur.(type) {
		case map[string]any:
			if seg.isIndex {
				return nil, false
			}
			v, ok := n[seg.key]
			if !ok {
				return nil, false
			}
			cur = v
		case Map:
			if seg.isIndex {
				return nil, false
			}
			v, ok := n[seg.key]
			if !ok {
				return nil, false
			}
			cur = v
		case []any:
			if !seg.isIndex || seg.append || seg.index < 0 || seg.index >= len(n) {
				return nil, false
			}
			cur = n[seg.index]
		default:
			return nil, false
		}
	}
	return cur, true
}

func toMapAnyOK(v any) (Map, bool) {
	switch x := v.(type) {
	case Map:
		return x, true
	case map[string]any:
		return Map(x), true
	default:
		return nil, false
	}
}

func toSliceAnyOK(v any) ([]any, bool) {
	switch x := v.(type) {
	case []any:
		return x, true
	case nil:
		return nil, false
	}
	rv := reflect.ValueOf(v)
	if rv.Kind() != reflect.Slice && rv.Kind() != reflect.Array {
		return nil, false
	}
	out := make([]any, rv.Len())
	for i := 0; i < rv.Len(); i++ {
		out[i] = rv.Index(i).Interface()
	}
	return out, true
}

func toStringOK(v any) (string, bool) {
	switch x := v.(type) {
	case nil:
		return "", false
	case string:
		return x, true
	case []byte:
		return string(x), true
	case fmt.Stringer:
		return x.String(), true
	}
	rv := reflect.ValueOf(v)
	switch rv.Kind() {
	case reflect.Bool:
		return strconv.FormatBool(rv.Bool()), true
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return strconv.FormatInt(rv.Int(), 10), true
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		return strconv.FormatUint(rv.Uint(), 10), true
	case reflect.Float32:
		return strconv.FormatFloat(rv.Float(), 'f', -1, 32), true
	case reflect.Float64:
		return strconv.FormatFloat(rv.Float(), 'f', -1, 64), true
	case reflect.String:
		return rv.String(), true
	default:
		return "", false
	}
}

func toInt64OK(v any) (int64, bool) {
	switch x := v.(type) {
	case nil:
		return 0, false
	case string:
		s := strings.TrimSpace(x)
		if i, err := strconv.ParseInt(s, 10, 64); err == nil {
			return i, true
		}
		if f, err := strconv.ParseFloat(s, 64); err == nil && f == math.Trunc(f) && f >= math.MinInt64 && f <= math.MaxInt64 {
			return int64(f), true
		}
		return 0, false
	}
	rv := reflect.ValueOf(v)
	switch rv.Kind() {
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return rv.Int(), true
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		u := rv.Uint()
		if u > math.MaxInt64 {
			return 0, false
		}
		return int64(u), true
	case reflect.Float32, reflect.Float64:
		f := rv.Float()
		if math.IsNaN(f) || f != math.Trunc(f) || f < math.MinInt64 || f > math.MaxInt64 {
			return 0, false
		}
		return int64(f), true
	case reflect.String:
		return toInt64OK(rv.String())
	default:
		return 0, false
	}
}

func toFloat64OK(v any) (float64, bool) {
	switch x := v.(type) {
	case nil:
		return 0, false
	case string:
		f, err := strconv.ParseFloat(strings.TrimSpace(x), 64)
		return f, err == nil
	}
	rv := reflect.ValueOf(v)
	switch rv.Kind() {
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return float64(rv.Int()), true
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		return float64(rv.Uint()), true
	case reflect.Float32, reflect.Float64:
		return rv.Float(), true
	case reflect.String:
		return toFloat64OK(rv.String())
	default:
		return 0, false
	}
}

func toBoolOK(v any) (bool, bool) {
	switch x := v.(type) {
	case nil:
		return false, false
	case bool:
		return x, true
	case string:
		b, err := strconv.ParseBool(strings.TrimSpace(x))
		return b, err == nil
	}
	rv := reflect.ValueOf(v)
	switch rv.Kind() {
	case reflect.Bool:
		return rv.Bool(), true
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return rv.Int() != 0, true
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		return rv.Uint() != 0, true
	case reflect.Float32, reflect.Float64:
		return rv.Float() != 0, true
	case reflect.String:
		return toBoolOK(rv.String())
	default:
		return false, false
	}
}

func (m Map) Object(path string) Map {
	if out, ok := toMapAnyOK(m.Get(path)); ok {
		return out
	}
	return nil
}

func (m Map) ObjectOK(path string) (Map, bool) {
	return toMapAnyOK(m.Get(path))
}

func (m Map) Array(path string) []any {
	if out, ok := toSliceAnyOK(m.Get(path)); ok {
		return out
	}
	return nil
}

func (m Map) ArrayOK(path string) ([]any, bool) {
	return toSliceAnyOK(m.Get(path))
}

func (m Map) Strings(path string) []string {
	arr, ok := toSliceAnyOK(m.Get(path))
	if !ok {
		return nil
	}
	out := make([]string, 0, len(arr))
	for _, v := range arr {
		if s, ok := toStringOK(v); ok {
			out = append(out, s)
		}
	}
	return out
}

func (m Map) StringOK(path string) (string, bool) {
	return toStringOK(m.Get(path))
}

func (m Map) String(path string, def ...string) string {
	if s, ok := toStringOK(m.Get(path)); ok {
		return s
	}
	if len(def) > 0 {
		return def[0]
	}
	return ""
}

func (m Map) IntOK(path string) (int, bool) {
	n, ok := toInt64OK(m.Get(path))
	if !ok || int64(int(n)) != n {
		return 0, false
	}
	return int(n), true
}

func (m Map) Int(path string, def ...int) int {
	if n, ok := m.IntOK(path); ok {
		return n
	}
	if len(def) > 0 {
		return def[0]
	}
	return 0
}

func (m Map) Int64OK(path string) (int64, bool) {
	return toInt64OK(m.Get(path))
}

func (m Map) Int64(path string, def ...int64) int64 {
	if n, ok := toInt64OK(m.Get(path)); ok {
		return n
	}
	if len(def) > 0 {
		return def[0]
	}
	return 0
}

func (m Map) Float64OK(path string) (float64, bool) {
	return toFloat64OK(m.Get(path))
}

func (m Map) Float64(path string, def ...float64) float64 {
	if f, ok := toFloat64OK(m.Get(path)); ok {
		return f
	}
	if len(def) > 0 {
		return def[0]
	}
	return 0
}

func (m Map) BoolOK(path string) (bool, bool) {
	return toBoolOK(m.Get(path))
}

func (m Map) Bool(path string, def ...bool) bool {
	if b, ok := toBoolOK(m.Get(path)); ok {
		return b
	}
	if len(def) > 0 {
		return def[0]
	}
	return false
}

package fluentmap

import (
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
)

func parseIndex(seg string) (int, bool) {
	if seg == "" {
		return 0, false
	}
	i, err := strconv.Atoi(seg)
	if err != nil || i < 0 {
		return 0, false
	}
	return i, true
}

// toString converts v to a string. nil yields "", byte slices are converted
// directly, and everything else is formatted with fmt.Sprintf.
func toString(v interface{}) string {
	switch t := v.(type) {
	case nil:
		return ""
	case string:
		return t
	case []byte:
		return string(t)
	case json.Number:
		return t.String()
	case fmt.Stringer:
		return t.String()
	case error:
		return t.Error()
	default:
		return fmt.Sprintf("%v", t)
	}
}

func toInt64(v interface{}) (int64, bool) {
	switch t := v.(type) {
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
	case json.Number:
		if i, err := t.Int64(); err == nil {
			return i, true
		}
		if f, err := t.Float64(); err == nil {
			return int64(f), true
		}
		return 0, false
	case bool:
		if t {
			return 1, true
		}
		return 0, true
	case string:
		s := strings.TrimSpace(t)
		if i, err := strconv.ParseInt(s, 10, 64); err == nil {
			return i, true
		}
		if f, err := strconv.ParseFloat(s, 64); err == nil {
			return int64(f), true
		}
		return 0, false
	default:
		return 0, false
	}
}

func toFloat64(v interface{}) (float64, bool) {
	switch t := v.(type) {
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
	case float32:
		return float64(t), true
	case float64:
		return t, true
	case json.Number:
		f, err := t.Float64()
		return f, err == nil
	case bool:
		if t {
			return 1, true
		}
		return 0, true
	case string:
		f, err := strconv.ParseFloat(strings.TrimSpace(t), 64)
		return f, err == nil
	default:
		return 0, false
	}
}

func toBool(v interface{}) (bool, bool) {
	switch t := v.(type) {
	case bool:
		return t, true
	case string:
		b, err := strconv.ParseBool(strings.TrimSpace(t))
		return b, err == nil
	case json.Number:
		f, err := t.Float64()
		return f != 0, err == nil
	case int:
		return t != 0, true
	case int8:
		return t != 0, true
	case int16:
		return t != 0, true
	case int32:
		return t != 0, true
	case int64:
		return t != 0, true
	case uint:
		return t != 0, true
	case uint8:
		return t != 0, true
	case uint16:
		return t != 0, true
	case uint32:
		return t != 0, true
	case uint64:
		return t != 0, true
	case float32:
		return t != 0, true
	case float64:
		return t != 0, true
	default:
		return false, false
	}
}

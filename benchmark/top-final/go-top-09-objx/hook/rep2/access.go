package objx

import (
	"reflect"
	"strconv"
	"strings"
)

// splitIndex splits a selector part such as "items[0][1]" into its field
// name ("items") and its array indices ([0, 1]).
func splitIndex(part string) (name string, indices []int) {
	open := strings.IndexByte(part, '[')
	if open == -1 {
		return part, nil
	}
	name = part[:open]
	rest := part[open:]
	for len(rest) > 0 && rest[0] == '[' {
		close := strings.IndexByte(rest, ']')
		if close == -1 {
			break
		}
		if idx, err := strconv.Atoi(rest[1:close]); err == nil {
			indices = append(indices, idx)
		}
		rest = rest[close+1:]
	}
	return name, indices
}

// access navigates one selector part (a field name plus optional array
// indices) from current, returning nil if it can't be resolved.
func access(current interface{}, part string) interface{} {
	name, indices := splitIndex(part)
	if name != "" {
		switch m := current.(type) {
		case Map:
			current = m[name]
		case map[string]interface{}:
			current = m[name]
		default:
			return nil
		}
	}
	for _, idx := range indices {
		current = accessIndex(current, idx)
	}
	return current
}

// accessIndex returns the element at idx if current is a slice or array,
// or nil otherwise.
func accessIndex(current interface{}, idx int) interface{} {
	if current == nil {
		return nil
	}
	v := reflect.ValueOf(current)
	if v.Kind() != reflect.Slice && v.Kind() != reflect.Array {
		return nil
	}
	if idx < 0 || idx >= v.Len() {
		return nil
	}
	return v.Index(idx).Interface()
}

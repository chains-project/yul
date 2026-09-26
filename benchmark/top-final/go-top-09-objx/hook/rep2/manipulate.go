package objx

import "strings"

// Set assigns value at the dotted-path selector (e.g. "a.b.c"), creating
// any intermediate maps as needed, and returns the receiver for chaining.
// Set does not support array indices in the selector.
func (m Map) Set(selector string, value interface{}) Map {
	if selector == "" {
		return m
	}
	parts := strings.Split(selector, ".")
	cur := m
	for i, part := range parts {
		if i == len(parts)-1 {
			cur[part] = value
			return m
		}
		switch next := cur[part].(type) {
		case Map:
			cur = next
		case map[string]interface{}:
			converted := Map(next)
			cur[part] = converted
			cur = converted
		default:
			created := Map{}
			cur[part] = created
			cur = created
		}
	}
	return m
}

// Copy returns a shallow copy of the map.
func (m Map) Copy() Map {
	c := make(Map, len(m))
	for k, v := range m {
		c[k] = v
	}
	return c
}

// MergeHere shallow-merges other into m in place, overwriting any
// existing keys, and returns the receiver for chaining.
func (m Map) MergeHere(other Map) Map {
	for k, v := range other {
		m[k] = v
	}
	return m
}

// Merge returns a new map that is a shallow copy of m with other merged
// in, overwriting any existing keys. Neither m nor other is modified.
func (m Map) Merge(other Map) Map {
	return m.Copy().MergeHere(other)
}

// Exclude returns a new map containing all of m's keys except those
// listed.
func (m Map) Exclude(keys []string) Map {
	excluded := make(map[string]bool, len(keys))
	for _, k := range keys {
		excluded[k] = true
	}
	out := Map{}
	for k, v := range m {
		if !excluded[k] {
			out[k] = v
		}
	}
	return out
}

// Include returns a new map containing only the listed keys (those
// present in m).
func (m Map) Include(keys []string) Map {
	out := Map{}
	for _, k := range keys {
		if v, ok := m[k]; ok {
			out[k] = v
		}
	}
	return out
}

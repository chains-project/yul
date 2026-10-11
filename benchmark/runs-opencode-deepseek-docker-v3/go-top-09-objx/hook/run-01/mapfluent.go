package mapfluent

import "sort"

type Map map[string]any

func New() Map { return Map{} }

func From(m map[string]any) Map {
	if m == nil {
		return Map{}
	}
	return Map(m)
}

func FromAny(v any) (Map, bool) {
	switch x := v.(type) {
	case Map:
		return x, true
	case map[string]any:
		return Map(x), true
	default:
		return nil, false
	}
}

func Of(pairs ...any) Map {
	m := New()
	for i := 0; i+1 < len(pairs); i += 2 {
		key, ok := pairs[i].(string)
		if !ok {
			continue
		}
		m.Set(key, pairs[i+1])
	}
	return m
}

func (m Map) Raw() map[string]any { return map[string]any(m) }

func (m Map) Len() int { return len(m) }

func (m Map) IsEmpty() bool { return len(m) == 0 }

func (m Map) Keys() []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

func (m Map) Has(path string) bool {
	segs := parsePath(path)
	if len(segs) == 0 {
		return false
	}
	_, ok := lookup(map[string]any(m), segs)
	return ok
}

func (m Map) Get(path string) any {
	segs := parsePath(path)
	if len(segs) == 0 {
		return nil
	}
	v, _ := lookup(map[string]any(m), segs)
	return v
}

func (m Map) GetOr(path string, fallback any) any {
	segs := parsePath(path)
	if len(segs) == 0 {
		return fallback
	}
	if v, ok := lookup(map[string]any(m), segs); ok {
		return v
	}
	return fallback
}

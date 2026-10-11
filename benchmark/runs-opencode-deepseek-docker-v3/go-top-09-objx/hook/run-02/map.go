package mapx

import (
	"encoding/json"
	"sort"
)

type Map struct {
	data map[string]interface{}
}

func New(data map[string]interface{}) *Map {
	if data == nil {
		data = map[string]interface{}{}
	}
	return &Map{data: data}
}

func From(v interface{}) *Map {
	m, _ := asMap(v)
	return New(m)
}

func FromJSON(b []byte) (*Map, error) {
	m := map[string]interface{}{}
	if err := json.Unmarshal(b, &m); err != nil {
		return nil, err
	}
	return New(m), nil
}

func (m *Map) Data() map[string]interface{} {
	if m == nil {
		return nil
	}
	return m.data
}

func (m *Map) Len() int {
	if m == nil {
		return 0
	}
	return len(m.data)
}

func (m *Map) Keys() []string {
	if m == nil {
		return nil
	}
	keys := make([]string, 0, len(m.data))
	for k := range m.data {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

func (m *Map) Get(path string) *Value {
	if m == nil {
		return newValue(nil, false)
	}
	raw, ok := getPath(m.data, parsePath(path))
	return newValue(raw, ok)
}

func (m *Map) Has(path string) bool {
	if m == nil {
		return false
	}
	_, ok := getPath(m.data, parsePath(path))
	return ok
}

func (m *Map) Set(path string, value interface{}) *Map {
	if m == nil {
		return m
	}
	segs := parsePath(path)
	if len(segs) == 0 {
		if vm, ok := asMap(value); ok {
			m.data = vm
		}
		return m
	}
	if res, ok := asMap(setPath(m.data, segs, value)); ok {
		m.data = res
	}
	return m
}

func (m *Map) Delete(path string) *Map {
	if m == nil {
		return m
	}
	segs := parsePath(path)
	if len(segs) == 0 {
		return m
	}
	if res, ok := asMap(deletePath(m.data, segs)); ok {
		m.data = res
	}
	return m
}

func (m *Map) Clone() *Map {
	if m == nil {
		return nil
	}
	return New(deepCopy(m.data).(map[string]interface{}))
}

func (m *Map) Merge(others ...*Map) *Map {
	if m == nil {
		return m
	}
	for _, o := range others {
		if o == nil {
			continue
		}
		mergeMaps(m.data, o.data)
	}
	return m
}

func (m *Map) Each(fn func(key string, v *Value)) *Map {
	if m == nil || fn == nil {
		return m
	}
	for k, raw := range m.data {
		fn(k, newValue(raw, true))
	}
	return m
}

func (m *Map) Filter(fn func(key string, v *Value) bool) *Map {
	if m == nil {
		return m
	}
	out := make(map[string]interface{}, len(m.data))
	for k, raw := range m.data {
		if fn(k, newValue(raw, true)) {
			out[k] = raw
		}
	}
	return New(out)
}

func (m *Map) MarshalJSON() ([]byte, error) {
	if m == nil {
		return []byte("null"), nil
	}
	return json.Marshal(m.data)
}

func (m *Map) UnmarshalJSON(b []byte) error {
	return json.Unmarshal(b, &m.data)
}

func (m *Map) String() string {
	b, err := json.Marshal(m)
	if err != nil {
		return ""
	}
	return string(b)
}

func Get(data map[string]interface{}, path string) *Value {
	return New(data).Get(path)
}

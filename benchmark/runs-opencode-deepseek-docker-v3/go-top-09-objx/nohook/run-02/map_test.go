package fluentmap_test

import (
	"encoding/json"
	"reflect"
	"testing"

	"github.com/example/fluentmap"
)

func TestNewAndFrom(t *testing.T) {
	a := fluentmap.New()
	if !a.IsEmpty() || a.Len() != 0 {
		t.Fatalf("expected empty map, got %v", a)
	}

	a = fluentmap.New(
		map[string]interface{}{"a": 1, "b": 2},
		map[string]interface{}{"b": 3},
	)
	if got, _ := a.GetInt("a"); got != 1 {
		t.Fatalf("a = %d, want 1", got)
	}
	if got, _ := a.GetInt("b"); got != 3 {
		t.Fatalf("b = %d, want 3 (later map wins)", got)
	}

	raw := map[string]interface{}{"x": 1}
	from := fluentmap.From(raw)
	from.Set("y", 2)
	if _, ok := raw["y"]; !ok {
		t.Fatal("From should wrap, not copy")
	}
}

func TestSetGetDelete(t *testing.T) {
	m := fluentmap.New().Set("name", "gopher").Set("age", 3)
	if !m.Has("name") || m.Has("nope") {
		t.Fatal("Has returned unexpected result")
	}
	if v, ok := m.Get("name"); !ok || v != "gopher" {
		t.Fatalf("Get(name) = %v, %v", v, ok)
	}
	if m.MustGet("missing") != nil {
		t.Fatal("MustGet on missing key should be nil")
	}

	m.SetDefault("name", "other").SetDefault("lang", "go")
	if s, _ := m.GetString("name"); s != "gopher" {
		t.Fatalf("SetDefault overwrote existing value: %s", s)
	}
	if s, _ := m.GetString("lang"); s != "go" {
		t.Fatal("SetDefault did not set missing value")
	}

	m.Delete("age")
	if m.Has("age") {
		t.Fatal("Delete did not remove key")
	}

	if keys := m.Keys(); !reflect.DeepEqual(keys, []string{"lang", "name"}) {
		t.Fatalf("Keys = %v, want sorted", keys)
	}

	m.Clear()
	if !m.IsEmpty() {
		t.Fatal("Clear did not empty the map")
	}
}

func TestTypedGetters(t *testing.T) {
	m := fluentmap.New(map[string]interface{}{
		"name":   "gopher",
		"age":    float64(3),
		"ratio":  "1.5",
		"ok":     "true",
		"tags":   []interface{}{"a", "b"},
		"ints":   []int{1, 2, 3},
		"nested": map[string]interface{}{"x": 1},
	})

	if s, ok := m.GetString("name"); !ok || s != "gopher" {
		t.Fatalf("GetString = %q, %v", s, ok)
	}
	if n, ok := m.GetInt("age"); !ok || n != 3 {
		t.Fatalf("GetInt = %d, %v", n, ok)
	}
	if n, ok := m.GetInt("ratio"); ok {
		t.Fatalf("GetInt on fractional value should fail, got %d", n)
	}
	if f, ok := m.GetFloat64("ratio"); !ok || f != 1.5 {
		t.Fatalf("GetFloat64 = %f, %v", f, ok)
	}
	if b, ok := m.GetBool("ok"); !ok || !b {
		t.Fatalf("GetBool = %v, %v", b, ok)
	}
	if tags, ok := m.GetStrings("tags"); !ok || !reflect.DeepEqual(tags, []string{"a", "b"}) {
		t.Fatalf("GetStrings = %v, %v", tags, ok)
	}
	if ints, ok := m.GetSlice("ints"); !ok || len(ints) != 3 {
		t.Fatalf("GetSlice = %v, %v", ints, ok)
	}

	inner, ok := m.GetMap("nested")
	if !ok {
		t.Fatal("GetMap failed")
	}
	inner.Set("y", 2)
	if v, _ := m.GetPathInt("nested.y"); v != 2 {
		t.Fatal("GetMap should wrap the nested map")
	}
}

func TestPathAccess(t *testing.T) {
	m := fluentmap.New()
	m.SetPath("a.b.c", 1)
	if v, ok := m.GetPathInt("a.b.c"); !ok || v != 1 {
		t.Fatalf("GetPathInt = %d, %v", v, ok)
	}
	if !m.HasPath("a.b") || m.HasPath("a.b.d") {
		t.Fatal("HasPath returned unexpected result")
	}

	m.SetPath("list[0].name", "first")
	m.SetPath("list[1].name", "second")
	if v, ok := m.GetPathString("list[1].name"); !ok || v != "second" {
		t.Fatalf("GetPathString = %q, %v", v, ok)
	}

	m.SetPath("matrix[1][0]", 9)
	if v, ok := m.GetPathInt("matrix[1][0]"); !ok || v != 9 {
		t.Fatalf("GetPathInt matrix = %d, %v", v, ok)
	}

	names, ok := m.GetPathStrings("list[0].name")
	if ok {
		t.Fatalf("GetPathStrings on non-slice should fail, got %v", names)
	}

	inner, ok := m.GetPathMap("a.b")
	if !ok {
		t.Fatal("GetPathMap failed")
	}
	if v, _ := inner.GetInt("c"); v != 1 {
		t.Fatal("GetPathMap returned wrong nested map")
	}

	m.DeletePath("a.b.c")
	if m.HasPath("a.b.c") {
		t.Fatal("DeletePath did not delete nested value")
	}

	m.DeletePath("list[0].name")
	if m.HasPath("list[0].name") {
		t.Fatal("DeletePath did not delete slice element")
	}
}

func TestMergeAndClone(t *testing.T) {
	m := fluentmap.New(map[string]interface{}{"a": 1, "b": 2})
	m.Merge(map[string]interface{}{"b": 3, "c": 4})
	if got, _ := m.GetInt("c"); got != 4 {
		t.Fatal("Merge did not add key")
	}
	if got, _ := m.GetInt("b"); got != 3 {
		t.Fatal("Merge did not overwrite key")
	}

	m.MergeMap(fluentmap.New(map[string]interface{}{"d": 5}))
	if got, _ := m.GetInt("d"); got != 5 {
		t.Fatal("MergeMap did not merge")
	}

	m.MergeDeep(map[string]interface{}{
		"nested": map[string]interface{}{"x": 1},
	})
	m.MergeDeep(map[string]interface{}{
		"nested": map[string]interface{}{"y": 2},
	})
	if v, _ := m.GetPathInt("nested.x"); v != 1 {
		t.Fatal("MergeDeep lost existing nested value")
	}
	if v, _ := m.GetPathInt("nested.y"); v != 2 {
		t.Fatal("MergeDeep did not add nested value")
	}

	clone := m.Clone()
	clone.SetPath("nested.x", 99)
	clone.Set("a", 99)
	if v, _ := m.GetPathInt("nested.x"); v != 1 {
		t.Fatal("Clone shares nested maps")
	}
	if v, _ := m.GetInt("a"); v != 1 {
		t.Fatal("Clone shares top-level values")
	}
	if clone.String() == m.String() {
		t.Fatal("expected clone and original to differ after mutation")
	}
}

func TestPickOmitFilterEach(t *testing.T) {
	m := fluentmap.New(map[string]interface{}{"a": 1, "b": 2, "c": 3})

	if p := m.Pick("a", "c", "zzz"); !reflect.DeepEqual(p.Value(), map[string]interface{}{"a": 1, "c": 3}) {
		t.Fatalf("Pick = %v", p)
	}
	if o := m.Omit("b"); !reflect.DeepEqual(o.Value(), map[string]interface{}{"a": 1, "c": 3}) {
		t.Fatalf("Omit = %v", o)
	}
	if f := m.Filter(func(k string, v interface{}) bool { return v.(int) > 1 }); !reflect.DeepEqual(f.Value(), map[string]interface{}{"b": 2, "c": 3}) {
		t.Fatalf("Filter = %v", f)
	}
	if m.Len() != 3 {
		t.Fatal("Filter/Pick/Omit should not modify the receiver")
	}

	var keys []string
	m.Each(func(k string, v interface{}) bool {
		keys = append(keys, k)
		return true
	})
	if !reflect.DeepEqual(keys, []string{"a", "b", "c"}) {
		t.Fatalf("Each keys = %v", keys)
	}

	count := 0
	m.Each(func(k string, v interface{}) bool {
		count++
		return count < 2
	})
	if count != 2 {
		t.Fatalf("Each early stop count = %d, want 2", count)
	}
}

func TestJSON(t *testing.T) {
	m := fluentmap.New().Set("a", 1).Set("b", []interface{}{"x", "y"})

	data, err := json.Marshal(m)
	if err != nil {
		t.Fatalf("Marshal: %v", err)
	}
	var back map[string]interface{}
	if err := json.Unmarshal(data, &back); err != nil {
		t.Fatalf("Unmarshal: %v", err)
	}
	if back["a"].(float64) != 1 {
		t.Fatalf("round trip a = %v", back["a"])
	}

	parsed, err := fluentmap.Parse([]byte(`{"x": true, "n": {"v": 7}}`))
	if err != nil {
		t.Fatalf("Parse: %v", err)
	}
	if b, ok := parsed.GetBool("x"); !ok || !b {
		t.Fatal("Parse did not populate bool")
	}
	if v, ok := parsed.GetPathInt("n.v"); !ok || v != 7 {
		t.Fatal("Parse did not populate nested value")
	}

	var target struct {
		X bool `json:"x"`
	}
	if err := parsed.Decode(&target); err != nil {
		t.Fatalf("Decode: %v", err)
	}
	if !target.X {
		t.Fatal("Decode did not populate struct")
	}

	var m2 fluentmap.Map
	if err := json.Unmarshal([]byte(`{"k":"v"}`), &m2); err != nil {
		t.Fatalf("UnmarshalJSON: %v", err)
	}
	if s, _ := m2.GetString("k"); s != "v" {
		t.Fatal("UnmarshalJSON did not populate map")
	}
}

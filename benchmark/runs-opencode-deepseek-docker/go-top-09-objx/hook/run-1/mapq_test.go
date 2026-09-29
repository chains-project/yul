package mapq

import (
	"encoding/json"
	"reflect"
	"testing"
)

func TestParsePath(t *testing.T) {
	tests := []struct {
		path string
		want []token
	}{
		{"", nil},
		{"a", []token{{key: "a"}}},
		{"a.b.c", []token{{key: "a"}, {key: "b"}, {key: "c"}}},
		{"items[0].name", []token{{key: "items"}, {index: 0, isIndex: true}, {key: "name"}}},
		{"items.0.name", []token{{key: "items"}, {index: 0, isIndex: true}, {key: "name"}}},
		{"a[2][3]", []token{{key: "a"}, {index: 2, isIndex: true}, {index: 3, isIndex: true}}},
		{`users[1]["first.name"]`, []token{{key: "users"}, {index: 1, isIndex: true}, {key: "first.name"}}},
		{"[0].x", []token{{index: 0, isIndex: true}, {key: "x"}}},
	}
	for _, tc := range tests {
		got, err := parsePath(tc.path)
		if err != nil {
			t.Fatalf("parsePath(%q) error: %v", tc.path, err)
		}
		if !reflect.DeepEqual(got, tc.want) {
			t.Errorf("parsePath(%q) = %#v, want %#v", tc.path, got, tc.want)
		}
	}
}

func TestParsePathErrors(t *testing.T) {
	for _, path := range []string{"a..b", "a[", "a[]", "a[-1]", "[x", "a[1"} {
		if _, err := parsePath(path); err == nil {
			t.Errorf("parsePath(%q) expected error, got nil", path)
		}
	}
}

func TestGet(t *testing.T) {
	m := New(map[string]interface{}{
		"user": map[string]interface{}{
			"name": "Ada",
			"tags": []interface{}{"a", "b", "c"},
		},
		"nil": nil,
	})

	tests := []struct {
		path  string
		want  interface{}
		found bool
	}{
		{"user.name", "Ada", true},
		{"user.tags[1]", "b", true},
		{"user.tags.2", "c", true},
		{"nil", nil, true},
		{"user.missing", nil, false},
		{"user.tags[9]", nil, false},
		{"user.name.first", nil, false},
	}
	for _, tc := range tests {
		got, ok := m.Get(tc.path)
		if ok != tc.found || got != tc.want {
			t.Errorf("Get(%q) = (%v, %v), want (%v, %v)", tc.path, got, ok, tc.want, tc.found)
		}
	}
}

func TestSetCreatesIntermediateContainers(t *testing.T) {
	m := New()
	m.Set("a.b.c", 1).
		Set("list[2]", "x").
		Set("list[0]", "y")

	if got := m.Int("a.b.c"); got != 1 {
		t.Errorf("a.b.c = %d, want 1", got)
	}
	if got := m.Data()["list"]; !reflect.DeepEqual(got, []interface{}{"y", nil, "x"}) {
		t.Errorf("list = %#v, want [y <nil> x]", got)
	}

	nested := m.GetOr("missing.deep", "fallback")
	if nested != "fallback" {
		t.Errorf("GetOr fallback = %v", nested)
	}
}

func TestSetDeepNested(t *testing.T) {
	data := map[string]interface{}{"a": map[string]interface{}{"b": 1}}
	m := New(data)
	m.Set("a.c.d", true)
	want := map[string]interface{}{
		"a": map[string]interface{}{"b": 1, "c": map[string]interface{}{"d": true}},
	}
	if !reflect.DeepEqual(m.Data(), want) {
		t.Errorf("data = %#v, want %#v", m.Data(), want)
	}
}

func TestDelete(t *testing.T) {
	m := New(map[string]interface{}{
		"a":    map[string]interface{}{"b": 1, "c": 2},
		"list": []interface{}{"x", "y", "z"},
	})
	m.Delete("a.b").Delete("list[0]")

	if m.Has("a.b") {
		t.Error("a.b should have been deleted")
	}
	if !m.Has("a.c") {
		t.Error("a.c should remain")
	}
	if got := m.Slice("list"); !reflect.DeepEqual(got, []interface{}{"y", "z"}) {
		t.Errorf("list = %#v, want [y z]", got)
	}
}

func TestTypedAccessors(t *testing.T) {
	m := New(map[string]interface{}{
		"str":    "hello",
		"num":    float64(42),
		"count":  "7",
		"bool":   "true",
		"f":      3.5,
		"list":   []interface{}{"a", "b"},
		"mixed":  []interface{}{map[string]interface{}{"nested": true}},
		"nested": map[string]interface{}{"x": 1},
		"nilval": nil,
	})

	if got := m.String("str", "def"); got != "hello" {
		t.Errorf("String = %q", got)
	}
	if got := m.String("missing", "def"); got != "def" {
		t.Errorf("String default = %q", got)
	}
	if got := m.Int("num"); got != 42 {
		t.Errorf("Int(num) = %d", got)
	}
	if got := m.Int("count"); got != 7 {
		t.Errorf("Int(count) = %d", got)
	}
	if got := m.Bool("bool"); !got {
		t.Error("Bool = false, want true")
	}
	if got := m.Float64("f"); got != 3.5 {
		t.Errorf("Float64 = %v", got)
	}
	if got := m.StringSlice("list"); !reflect.DeepEqual(got, []string{"a", "b"}) {
		t.Errorf("StringSlice = %#v", got)
	}
	if got := m.StringSlice("mixed"); got != nil {
		t.Errorf("StringSlice(mixed) = %#v, want nil", got)
	}
	if !m.IsNil("nilval") {
		t.Error("IsNil(nilval) = false")
	}
	if m.IsNil("missing") {
		t.Error("IsNil(missing) should be false")
	}

	sub, ok := m.Map("nested")
	if !ok || sub.Int("x") != 1 {
		t.Error("Map(nested) failed")
	}
	if got := m.Sub("missing").Len(); got != 0 {
		t.Errorf("Sub(missing).Len() = %d, want 0", got)
	}
}

func TestCloneIsDeep(t *testing.T) {
	m := New(map[string]interface{}{"a": map[string]interface{}{"b": 1}})
	c := m.Clone()
	c.Set("a.b", 2)
	if m.Int("a.b") != 1 {
		t.Error("Clone is not deep: original mutated")
	}
}

func TestMergeDeep(t *testing.T) {
	m := New(map[string]interface{}{
		"a":    map[string]interface{}{"b": 1, "c": 2},
		"keep": true,
	})
	other := New(map[string]interface{}{
		"a":   map[string]interface{}{"c": 3, "d": 4},
		"new": "x",
	})
	m.Merge(other)

	want := map[string]interface{}{
		"a":    map[string]interface{}{"b": 1, "c": 3, "d": 4},
		"keep": true,
		"new":  "x",
	}
	if !reflect.DeepEqual(m.Data(), want) {
		t.Errorf("merged = %#v, want %#v", m.Data(), want)
	}
}

func TestKeysForEachUpdateApply(t *testing.T) {
	m := New(map[string]interface{}{"b": 2, "a": 1, "c": 3})
	if got := m.Keys(); !reflect.DeepEqual(got, []string{"a", "b", "c"}) {
		t.Errorf("Keys = %#v", got)
	}

	var seen []string
	m.ForEach(func(k string, _ interface{}) bool {
		seen = append(seen, k)
		return k != "b"
	})
	if !reflect.DeepEqual(seen, []string{"a", "b"}) {
		t.Errorf("ForEach order/stop = %#v", seen)
	}

	m.Update("a", func(cur interface{}) interface{} { return cur.(int) + 10 })
	if m.Int("a") != 11 {
		t.Errorf("Update a = %d, want 11", m.Int("a"))
	}

	got := m.Apply(func(in *Map) *Map { return in.Set("d", 4) })
	if got.Int("d") != 4 {
		t.Error("Apply did not chain")
	}
}

func TestErrorLatching(t *testing.T) {
	m := New().Set("a.-1", 1)
	if m.Err() == nil {
		t.Fatal("expected parse error to be latched")
	}
	m.Set("b", 2)
	if m.Has("b") {
		t.Error("mutations after an error should be no-ops")
	}
	if out, err := m.ErrOrNil(); out != nil || err == nil {
		t.Error("ErrOrNil should return nil, err")
	}
	if _, err := m.Done(); err == nil {
		t.Error("Done should return the latched error")
	}
}

func TestJSONRoundTrip(t *testing.T) {
	m, err := FromJSON([]byte(`{"user":{"name":"Ada","age":36},"tags":["x","y"]}`))
	if err != nil {
		t.Fatal(err)
	}
	if m.String("user.name") != "Ada" || m.Int("user.age") != 36 {
		t.Errorf("decoded values wrong: %#v", m.Data())
	}
	if got := m.StringSlice("tags"); !reflect.DeepEqual(got, []string{"x", "y"}) {
		t.Errorf("tags = %#v", got)
	}

	raw, err := m.JSON()
	if err != nil {
		t.Fatal(err)
	}
	var back map[string]interface{}
	if err := json.Unmarshal(raw, &back); err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(back, m.Data()) {
		t.Errorf("round trip mismatch: %#v vs %#v", back, m.Data())
	}

	if _, err := FromJSON([]byte(`[1,2,3]`)); err == nil {
		t.Error("FromJSON should reject non-object documents")
	}
}

func TestUnmarshalJSON(t *testing.T) {
	m := New(map[string]interface{}{"old": true})
	if err := json.Unmarshal([]byte(`{"new":1}`), m); err != nil {
		t.Fatal(err)
	}
	if m.Has("old") || m.Int("new") != 1 {
		t.Errorf("UnmarshalJSON result = %#v", m.Data())
	}
}

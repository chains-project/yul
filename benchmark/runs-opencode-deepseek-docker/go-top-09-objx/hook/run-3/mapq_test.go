package mapq

import (
	"encoding/json"
	"reflect"
	"testing"
)

func TestGetOK(t *testing.T) {
	m := New(map[string]interface{}{
		"user": map[string]interface{}{
			"name": "Ada",
			"tags": []interface{}{"admin", "dev"},
			"meta": map[string]interface{}{"age": float64(36)},
		},
		"a.b": "escaped",
	})

	cases := []struct {
		path string
		want interface{}
		ok   bool
	}{
		{"user.name", "Ada", true},
		{"user.tags[0]", "admin", true},
		{"user.tags[1]", "dev", true},
		{"user.meta.age", float64(36), true},
		{`a\.b`, "escaped", true},
		{"missing.path", nil, false},
		{"user.tags[2]", nil, false},
		{"user.name.deep", nil, false},
		{"", map[string]interface{}(m), true},
	}

	for _, tc := range cases {
		got, ok := m.GetOK(tc.path)
		if ok != tc.ok {
			t.Errorf("GetOK(%q) ok = %v, want %v", tc.path, ok, tc.ok)
		}
		if !reflect.DeepEqual(got, tc.want) {
			t.Errorf("GetOK(%q) = %#v, want %#v", tc.path, got, tc.want)
		}
	}
}

func TestSetCreatesAndChains(t *testing.T) {
	m := New().
		Set("user.name", "Ada").
		Set("user.address.city", "London").
		Set("user.tags[0]", "admin").
		Set("user.tags[2]", "ops").
		Set("count", 3)

	if got := m.GetString("user.name"); got != "Ada" {
		t.Fatalf("user.name = %q", got)
	}
	if got := m.GetString("user.address.city"); got != "London" {
		t.Fatalf("city = %q", got)
	}
	tags := m.GetSlice("user.tags")
	if len(tags) != 3 || tags[0] != "admin" || tags[1] != nil || tags[2] != "ops" {
		t.Fatalf("tags = %#v", tags)
	}
	if got := m.GetInt("count"); got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestSetReplacesScalarWithContainer(t *testing.T) {
	m := New().Set("a", 1).Set("a.b.c", "deep")
	if got := m.GetString("a.b.c"); got != "deep" {
		t.Fatalf("got %q", got)
	}
}

func TestDelete(t *testing.T) {
	m := New(map[string]interface{}{
		"user": map[string]interface{}{
			"name": "Ada",
			"tags": []interface{}{"a", "b", "c"},
		},
	})

	m.Delete("user.name")
	if m.Has("user.name") {
		t.Fatal("user.name should be deleted")
	}

	m.Delete("user.tags[1]")
	if got := m.GetSlice("user.tags"); !reflect.DeepEqual(got, []interface{}{"a", "c"}) {
		t.Fatalf("tags = %#v", got)
	}

	m.Delete("nope.nope")
}

func TestMergeIsShallow(t *testing.T) {
	a := New(map[string]interface{}{"x": 1, "nested": map[string]interface{}{"a": 1}})
	b := New(map[string]interface{}{"x": 2, "y": 3, "nested": map[string]interface{}{"b": 2}})

	a.Merge(b)

	if a.GetInt("x") != 2 || a.GetInt("y") != 3 {
		t.Fatalf("merge failed: %#v", a)
	}
	if a.GetMap("nested").Has("a") {
		t.Fatal("shallow merge should replace nested map")
	}
}

func TestCloneIsDeep(t *testing.T) {
	orig := New(map[string]interface{}{
		"nested": map[string]interface{}{"list": []interface{}{1, 2}},
	})
	cp := orig.Clone()

	cp.Set("nested.list[0]", 99).Set("nested.new", true)

	if orig.GetSlice("nested.list")[0] != 1 {
		t.Fatal("clone shares nested slice")
	}
	if orig.GetMap("nested").Has("new") {
		t.Fatal("clone shares nested map")
	}
}

func TestTypedGetters(t *testing.T) {
	m := New(map[string]interface{}{
		"s": "hello",
		"i": float64(42),
		"f": "3.5",
		"b": "true",
		"x": struct{}{},
	})

	if got := m.GetString("s"); got != "hello" {
		t.Errorf("String = %q", got)
	}
	if got := m.GetInt("i"); got != 42 {
		t.Errorf("Int = %d", got)
	}
	if got := m.GetFloat64("f"); got != 3.5 {
		t.Errorf("Float64 = %v", got)
	}
	if got := m.GetBool("b"); got != true {
		t.Errorf("Bool = %v", got)
	}
	if _, ok := m.GetStringOK("i"); ok {
		t.Error("StringOK should reject non-string")
	}
	if _, ok := m.GetIntOK("s"); ok {
		t.Error("IntOK should reject non-numeric string")
	}
	if _, ok := m.GetBoolOK("x"); ok {
		t.Error("BoolOK should reject unsupported type")
	}
}

func TestKeysSorted(t *testing.T) {
	m := New(map[string]interface{}{"c": 1, "a": 2, "b": 3})
	if got := m.Keys(); !reflect.DeepEqual(got, []string{"a", "b", "c"}) {
		t.Fatalf("Keys = %#v", got)
	}
}

func TestJSONRoundTrip(t *testing.T) {
	raw := []byte(`{"user":{"name":"Ada","age":36},"ok":true}`)
	m, err := FromJSON(raw)
	if err != nil {
		t.Fatal(err)
	}
	if m.GetString("user.name") != "Ada" || m.GetInt("user.age") != 36 || !m.GetBool("ok") {
		t.Fatalf("decoded = %#v", m)
	}

	out, err := json.Marshal(m)
	if err != nil {
		t.Fatal(err)
	}
	var back Map
	if err := json.Unmarshal(out, &back); err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(m, back) {
		t.Fatalf("round trip mismatch: %s vs %s", m, back)
	}
}

func TestNilMapReadsAreSafe(t *testing.T) {
	var m Map
	if m.Has("a") || m.Get("a") != nil || m.GetString("a") != "" {
		t.Fatal("nil map reads should be safe")
	}
	if m.Set("a", 1) != nil {
		t.Fatal("Set on nil map should be a no-op returning nil")
	}
}

func TestParsePath(t *testing.T) {
	cases := []struct {
		path string
		want []segment
	}{
		{"a.b", []segment{{key: "a"}, {key: "b"}}},
		{"a[0].b", []segment{{key: "a"}, {index: 0, isIdx: true}, {key: "b"}}},
		{`a\.b`, []segment{{key: "a.b"}}},
		{"[2]", []segment{{index: 2, isIdx: true}}},
	}
	for _, tc := range cases {
		if got := parsePath(tc.path); !reflect.DeepEqual(got, tc.want) {
			t.Errorf("parsePath(%q) = %#v, want %#v", tc.path, got, tc.want)
		}
	}
}

package mapfluent_test

import (
	"encoding/json"
	"reflect"
	"testing"

	"mapfluent"
)

func TestNewSetGet(t *testing.T) {
	m := mapfluent.New().
		Set("name", "Ada").
		Set("age", 36)

	if got := m.Get("name").String(); got != "Ada" {
		t.Fatalf("name = %q, want Ada", got)
	}
	if got := m.Get("age").Int(); got != 36 {
		t.Fatalf("age = %d, want 36", got)
	}
	if !m.Has("name") {
		t.Fatal("Has(name) = false, want true")
	}
	if m.Has("missing") {
		t.Fatal("Has(missing) = true, want false")
	}
	if m.Get("missing").Exists() {
		t.Fatal("Get(missing).Exists() = true, want false")
	}
	if got := m.Len(); got != 2 {
		t.Fatalf("Len() = %d, want 2", got)
	}
}

func TestNewBacksProvidedMap(t *testing.T) {
	raw := map[string]interface{}{"a": 1}
	m := mapfluent.New(raw)
	m.Set("b", 2)
	if _, ok := raw["b"]; !ok {
		t.Fatal("mutation did not propagate to the provided map")
	}
	if m.Object()["a"].(int) != 1 {
		t.Fatal("provided map not used as backing store")
	}
}

func TestGetVariadic(t *testing.T) {
	m := mapfluent.Wrap(map[string]interface{}{
		"a": map[string]interface{}{"b": map[string]interface{}{"c": 42}},
	})
	if got := m.Get("a", "b", "c").Int(); got != 42 {
		t.Fatalf("nested Get = %d, want 42", got)
	}
	if got := m.GetPath("a.b.c").Int(); got != 42 {
		t.Fatalf("GetPath = %d, want 42", got)
	}
}

func TestMissingChainIsSafe(t *testing.T) {
	m := mapfluent.New(map[string]interface{}{"a": map[string]interface{}{}})
	got := m.GetPath("a.missing.deep.value")
	if got.Exists() {
		t.Fatal("missing path reported as existing")
	}
	if s := got.String(); s != "" {
		t.Fatalf("String() = %q, want empty", s)
	}
	if got.Int() != 0 || got.Bool() || got.Float64() != 0 {
		t.Fatal("zero values not returned for missing path")
	}
}

func TestGetPathArraysAndQuotedKeys(t *testing.T) {
	doc, err := mapfluent.FromJSON([]byte(`{
		"users": [{"name": "Ada"}, {"name": "Alan"}],
		"meta": {"a.b": "dotted"}
	}`))
	if err != nil {
		t.Fatal(err)
	}
	if got := doc.GetPath("users[1].name").String(); got != "Alan" {
		t.Fatalf("users[1].name = %q, want Alan", got)
	}
	if got := doc.GetPath(`meta["a.b"]`).String(); got != "dotted" {
		t.Fatalf("quoted key = %q, want dotted", got)
	}
	if got := doc.GetPath("users[0].name").String(); got != "Ada" {
		t.Fatalf("users[0].name = %q, want Ada", got)
	}
}

func TestSetPathCreatesIntermediates(t *testing.T) {
	m := mapfluent.New()
	m.SetPath("a.b.c", 1).SetPath("a.b.d", 2).SetPath("a.e[0]", 3)

	if got := m.GetPath("a.b.c").Int(); got != 1 {
		t.Fatalf("a.b.c = %d, want 1", got)
	}
	if got := m.GetPath("a.b.d").Int(); got != 2 {
		t.Fatalf("a.b.d = %d, want 2", got)
	}
	if got := m.GetPath("a.e[0]").Int(); got != 3 {
		t.Fatalf("a.e[0] = %d, want 3", got)
	}
}

func TestSetPathReplacesScalar(t *testing.T) {
	m := mapfluent.New(map[string]interface{}{"a": "scalar"})
	m.SetPath("a.b.c", 7)
	if !m.Get("a").IsObject() {
		t.Fatal("scalar was not replaced by an object")
	}
	if got := m.GetPath("a.b.c").Int(); got != 7 {
		t.Fatalf("a.b.c = %d, want 7", got)
	}
}

func TestSetOnNonObjectRoot(t *testing.T) {
	m := mapfluent.Wrap("scalar").Set("k", "v")
	if got := m.Get("k").String(); got != "v" {
		t.Fatalf("k = %q, want v", got)
	}
}

func TestSetArrayIndex(t *testing.T) {
	m := mapfluent.New(map[string]interface{}{"xs": []interface{}{1, 2}})
	m.SetPath("xs[1]", 20)
	m.SetPath("xs[2]", 30) // append at len
	if got := m.GetPath("xs").Array(); !reflect.DeepEqual(got, []interface{}{1, 20, 30}) {
		t.Fatalf("xs = %#v", got)
	}
}

func TestDelete(t *testing.T) {
	m := mapfluent.New(map[string]interface{}{
		"a": map[string]interface{}{"b": 1, "c": 2},
		"d": []interface{}{"x", "y", "z"},
	})
	m.Delete("nope")
	m.DeletePath("a.b")
	m.DeletePath("d[1]")

	if m.HasPath("a.b") {
		t.Fatal("a.b still present")
	}
	if got := m.GetPath("a.c").Int(); got != 2 {
		t.Fatalf("a.c = %d, want 2", got)
	}
	if got := m.GetPath("d").Array(); !reflect.DeepEqual(got, []interface{}{"x", "z"}) {
		t.Fatalf("d = %#v", got)
	}
}

func TestTypedConversions(t *testing.T) {
	m := mapfluent.New(map[string]interface{}{
		"strNum":  "42",
		"strF":    "3.5",
		"float":   2.9,
		"boolStr": "true",
		"boolNum": 1,
		"negBool": 0,
		"nil":     nil,
		"u16":     uint16(7),
	})

	tests := []struct {
		name string
		got  interface{}
		want interface{}
	}{
		{"strNum.Int", m.Get("strNum").Int(), 42},
		{"strF.Float", m.Get("strF").Float64(), 3.5},
		{"float.Int", m.Get("float").Int(), 2},
		{"boolStr.Bool", m.Get("boolStr").Bool(), true},
		{"boolNum.Bool", m.Get("boolNum").Bool(), true},
		{"negBool.Bool", m.Get("negBool").Bool(), false},
		{"u16.Int", m.Get("u16").Int(), 7},
		{"nil.IsNil", m.Get("nil").IsNil(), true},
		{"nil.IntOr", m.Get("nil").IntOr(9), 9},
		{"missing.StringOr", m.Get("missing").StringOr("x"), "x"},
		{"missing.BoolOr", m.Get("missing").BoolOr(true), true},
		{"missing.Float64Or", m.Get("missing").Float64Or(1.5), 1.5},
	}
	for _, tt := range tests {
		if !reflect.DeepEqual(tt.got, tt.want) {
			t.Errorf("%s = %#v, want %#v", tt.name, tt.got, tt.want)
		}
	}
}

func TestStringSlice(t *testing.T) {
	m := mapfluent.Wrap([]interface{}{"a", 1, true})
	if got := m.StringSlice(); !reflect.DeepEqual(got, []string{"a", "1", "true"}) {
		t.Fatalf("StringSlice = %#v", got)
	}
	if got := mapfluent.Wrap("solo").StringSlice(); !reflect.DeepEqual(got, []string{"solo"}) {
		t.Fatalf("scalar StringSlice = %#v", got)
	}
}

func TestKeysSorted(t *testing.T) {
	m := mapfluent.New(map[string]interface{}{"c": 1, "a": 2, "b": 3})
	if got := m.Keys(); !reflect.DeepEqual(got, []string{"a", "b", "c"}) {
		t.Fatalf("Keys = %#v", got)
	}
	if got := mapfluent.Wrap([]interface{}{"x", "y"}).Keys(); !reflect.DeepEqual(got, []string{"0", "1"}) {
		t.Fatalf("array Keys = %#v", got)
	}
}

func TestEach(t *testing.T) {
	m := mapfluent.New(map[string]interface{}{"a": 1, "b": 2, "c": 3})
	var seen []string
	m.Each(func(key string, value *mapfluent.Map) bool {
		if value.Int() >= 3 {
			return false
		}
		seen = append(seen, key)
		return true
	})
	if !reflect.DeepEqual(seen, []string{"a", "b"}) {
		t.Fatalf("seen = %#v", seen)
	}
}

func TestMergeDeep(t *testing.T) {
	a := mapfluent.New(map[string]interface{}{
		"nested": map[string]interface{}{"keep": 1, "over": 1},
		"flat":   1,
	})
	b := mapfluent.New(map[string]interface{}{
		"nested": map[string]interface{}{"over": 2, "new": 3},
		"flat":   2,
	})
	a.Merge(b)

	if got := a.GetPath("nested.keep").Int(); got != 1 {
		t.Fatalf("nested.keep = %d, want 1", got)
	}
	if got := a.GetPath("nested.over").Int(); got != 2 {
		t.Fatalf("nested.over = %d, want 2", got)
	}
	if got := a.GetPath("nested.new").Int(); got != 3 {
		t.Fatalf("nested.new = %d, want 3", got)
	}
	if got := a.Get("flat").Int(); got != 2 {
		t.Fatalf("flat = %d, want 2", got)
	}
	// b must not be mutated by the merge.
	if got := b.GetPath("nested.keep"); got.Exists() {
		t.Fatal("source mutated by Merge")
	}
}

func TestCloneIsDeep(t *testing.T) {
	orig := mapfluent.New(map[string]interface{}{
		"nested": map[string]interface{}{"a": []interface{}{1, 2}},
	})
	clone := orig.Clone()
	clone.SetPath("nested.a[0]", 99)
	clone.Set("top", true)

	if got := orig.GetPath("nested.a[0]").Int(); got != 1 {
		t.Fatalf("original mutated through clone: %d", got)
	}
	if orig.Has("top") {
		t.Fatal("top leaked into original")
	}
}

func TestJSONRoundTrip(t *testing.T) {
	src := `{"a":1,"b":["x","y"],"c":{"d":true}}`
	m, err := mapfluent.FromJSON([]byte(src))
	if err != nil {
		t.Fatal(err)
	}
	out, err := m.ToJSON()
	if err != nil {
		t.Fatal(err)
	}
	var want, got map[string]interface{}
	if err := json.Unmarshal([]byte(src), &want); err != nil {
		t.Fatal(err)
	}
	if err := json.Unmarshal(out, &got); err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("round trip mismatch: %v vs %v", want, got)
	}
	if _, err := m.ToJSONIndent("", "  "); err != nil {
		t.Fatal(err)
	}
	if s := m.JSONString(); s == "" {
		t.Fatal("JSONString returned empty")
	}
}

func TestFromJSONError(t *testing.T) {
	if _, err := mapfluent.FromJSON([]byte("{")); err == nil {
		t.Fatal("expected error for invalid JSON")
	}
}

func TestDecode(t *testing.T) {
	m := mapfluent.New(map[string]interface{}{"Name": "Ada", "Age": 36})
	var out struct {
		Name string
		Age  int
	}
	if err := m.Decode(&out); err != nil {
		t.Fatal(err)
	}
	if out.Name != "Ada" || out.Age != 36 {
		t.Fatalf("decoded = %#v", out)
	}
}

func TestArrayAndObject(t *testing.T) {
	if got := mapfluent.Wrap([]interface{}{1}).Array(); len(got) != 1 {
		t.Fatalf("Array = %#v", got)
	}
	if got := mapfluent.Wrap("x").Array(); got != nil {
		t.Fatalf("non-array Array = %#v", got)
	}
	if got := mapfluent.Wrap(map[string]interface{}{"k": 1}).Object(); got["k"] != 1 {
		t.Fatalf("Object = %#v", got)
	}
	if got := mapfluent.Wrap(1).Object(); got != nil {
		t.Fatalf("non-object Object = %#v", got)
	}
}

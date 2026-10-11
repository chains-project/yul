package mapx

import (
	"encoding/json"
	"reflect"
	"testing"
	"time"
)

func TestNewAndOf(t *testing.T) {
	if !New().IsEmpty() {
		t.Fatal("New should be empty")
	}
	if !Of(nil).IsEmpty() {
		t.Fatal("Of(nil) should be empty")
	}

	src := map[string]interface{}{"a": 1}
	m := Of(src)
	if m.Len() != 1 {
		t.Fatalf("Len = %d, want 1", m.Len())
	}
	m.Set("b", 2)
	if src["b"] != 2 {
		t.Fatal("Of should share the underlying map")
	}
	if !reflect.DeepEqual(m.Raw(), src) {
		t.Fatalf("Raw = %v, want %v", m.Raw(), src)
	}
}

func TestAccessAndMutation(t *testing.T) {
	m := New().Set("name", "Ada").Set("age", 36)

	if got := m.Get("name"); got != "Ada" {
		t.Fatalf("Get = %v", got)
	}
	if v, ok := m.GetOk("missing"); ok || v != nil {
		t.Fatal("GetOk on missing key should be nil,false")
	}
	if !m.Has("age") || m.Has("nope") {
		t.Fatal("Has mismatch")
	}
	if got := m.GetOr("missing", "fallback"); got != "fallback" {
		t.Fatalf("GetOr = %v", got)
	}
	if got := m.GetOr("name", "fallback"); got != "Ada" {
		t.Fatalf("GetOr existing = %v", got)
	}

	m.Delete("age")
	if m.Has("age") {
		t.Fatal("Delete failed")
	}

	if !reflect.DeepEqual(m.Keys(), []string{"name"}) {
		t.Fatalf("Keys = %v", m.Keys())
	}
	if !reflect.DeepEqual(m.Values(), []interface{}{"Ada"}) {
		t.Fatalf("Values = %v", m.Values())
	}
}

func TestKeysSorted(t *testing.T) {
	m := Of(map[string]interface{}{"c": 3, "a": 1, "b": 2})
	if !reflect.DeepEqual(m.Keys(), []string{"a", "b", "c"}) {
		t.Fatalf("Keys not sorted: %v", m.Keys())
	}
	if !reflect.DeepEqual(m.Values(), []interface{}{1, 2, 3}) {
		t.Fatalf("Values not key-ordered: %v", m.Values())
	}
}

func TestOnlyExcept(t *testing.T) {
	m := Of(map[string]interface{}{"a": 1, "b": 2, "c": 3})

	if got := m.Only("a", "c", "z"); !reflect.DeepEqual(got.Raw(), map[string]interface{}{"a": 1, "c": 3}) {
		t.Fatalf("Only = %v", got.Raw())
	}
	if got := m.Except("b"); !reflect.DeepEqual(got.Raw(), map[string]interface{}{"a": 1, "c": 3}) {
		t.Fatalf("Except = %v", got.Raw())
	}
	if len(m.Raw()) != 3 {
		t.Fatal("Only/Except must not mutate the receiver")
	}
}

func TestTransforms(t *testing.T) {
	m := Of(map[string]interface{}{"a": 1, "b": 2, "c": 3})

	filtered := m.Filter(func(_ string, v interface{}) bool { return v.(int) > 1 })
	if !reflect.DeepEqual(filtered.Raw(), map[string]interface{}{"b": 2, "c": 3}) {
		t.Fatalf("Filter = %v", filtered.Raw())
	}

	rejected := m.Reject(func(_ string, v interface{}) bool { return v.(int) > 1 })
	if !reflect.DeepEqual(rejected.Raw(), map[string]interface{}{"a": 1}) {
		t.Fatalf("Reject = %v", rejected.Raw())
	}

	doubled := m.Transform(func(_ string, v interface{}) interface{} { return v.(int) * 2 })
	if !reflect.DeepEqual(doubled.Raw(), map[string]interface{}{"a": 2, "b": 4, "c": 6}) {
		t.Fatalf("Transform = %v", doubled.Raw())
	}

	upper := m.MapKeys(func(k string, _ interface{}) string { return k + "!" })
	if !reflect.DeepEqual(upper.Keys(), []string{"a!", "b!", "c!"}) {
		t.Fatalf("MapKeys = %v", upper.Keys())
	}

	sum := 0
	chained := m.Each(func(_ string, v interface{}) { sum += v.(int) })
	if sum != 6 {
		t.Fatalf("Each sum = %d", sum)
	}
	if chained.Len() != 3 {
		t.Fatal("Each should return the receiver for chaining")
	}
}

func TestMerge(t *testing.T) {
	m := Of(map[string]interface{}{
		"a": 1,
		"nested": map[string]interface{}{
			"x": 1,
		},
	})
	other := map[string]interface{}{
		"b": 2,
		"nested": map[string]interface{}{
			"y": 2,
		},
	}

	shallow := m.Clone().Merge(other)
	nested := shallow.Get("nested").(map[string]interface{})
	if _, ok := nested["x"]; ok {
		t.Fatalf("shallow merge should replace nested map: %v", nested)
	}

	deep := m.Clone().MergeRecursive(other)
	nested = deep.Get("nested").(map[string]interface{})
	if nested["x"] != 1 || nested["y"] != 2 {
		t.Fatalf("deep merge nested = %v", nested)
	}
}

func TestMergeAcceptsMap(t *testing.T) {
	m := New().Set("a", 1)
	m.Merge(Of(map[string]interface{}{"b": 2}))
	m.MergeRecursive(Of(map[string]interface{}{"c": 3}))
	if m.GetInt("a") != 1 || m.GetInt("b") != 2 || m.GetInt("c") != 3 {
		t.Fatalf("merge with Map = %v", m)
	}
}

func TestCleanAndClone(t *testing.T) {
	m := Of(map[string]interface{}{
		"keep":  1,
		"nil":   nil,
		"empty": "",
		"list":  []interface{}{},
		"obj":   map[string]interface{}{},
	})
	cleaned := m.Clean()
	if !reflect.DeepEqual(cleaned.Raw(), map[string]interface{}{"keep": 1}) {
		t.Fatalf("Clean = %v", cleaned.Raw())
	}

	original := Of(map[string]interface{}{
		"nested": map[string]interface{}{"x": 1},
		"list":   []interface{}{1, 2},
	})
	clone := original.Clone()
	clone.GetMap("nested").Set("x", 99)
	clone.GetSlice("list")[0] = 99

	if original.PathInt("nested.x") != 1 {
		t.Fatal("Clone must deep-copy nested maps")
	}
	if original.GetSlice("list")[0] != 1 {
		t.Fatal("Clone must deep-copy slices")
	}
}

func TestTypedGetters(t *testing.T) {
	m := Of(map[string]interface{}{
		"str":      "hello",
		"numstr":   "42",
		"floatstr": "3.5",
		"int":      7,
		"float":    2.5,
		"bool":     true,
		"boolstr":  "true",
		"zero":     0,
		"nested":   map[string]interface{}{"k": "v"},
		"slice":    []interface{}{1, "two", true},
		"strings":  []string{"a", "b"},
		"time":     "2024-01-02T15:04:05Z",
		"unix":     1704207845,
		"durstr":   "1h30m",
		"durnum":   int64(90 * time.Second),
	})

	if got := m.GetString("int"); got != "7" {
		t.Fatalf("GetString(int) = %q", got)
	}
	if got := m.GetInt("numstr"); got != 42 {
		t.Fatalf("GetInt = %d", got)
	}
	if got := m.GetInt("floatstr"); got != 3 {
		t.Fatalf("GetInt(floatstr) = %d", got)
	}
	if got := m.GetInt64("int"); got != 7 {
		t.Fatalf("GetInt64 = %d", got)
	}
	if got := m.GetFloat64("float"); got != 2.5 {
		t.Fatalf("GetFloat64 = %v", got)
	}
	if !m.GetBool("bool") || !m.GetBool("boolstr") || m.GetBool("zero") {
		t.Fatal("GetBool mismatch")
	}
	if got := m.GetString("missing"); got != "" {
		t.Fatalf("GetString missing = %q", got)
	}
	if got := m.GetMap("nested"); got.GetString("k") != "v" {
		t.Fatalf("GetMap = %v", got)
	}
	if got := m.GetSlice("slice"); len(got) != 3 || got[1] != "two" {
		t.Fatalf("GetSlice = %v", got)
	}
	if got := m.GetStrings("strings"); !reflect.DeepEqual(got, []string{"a", "b"}) {
		t.Fatalf("GetStrings = %v", got)
	}
	want := time.Date(2024, 1, 2, 15, 4, 5, 0, time.UTC)
	if got := m.GetTime("time"); !got.Equal(want) {
		t.Fatalf("GetTime = %v", got)
	}
	if got := m.GetTime("unix"); got.Unix() != 1704207845 {
		t.Fatalf("GetTime unix = %v", got)
	}
	if got := m.GetDuration("durstr"); got != 90*time.Minute {
		t.Fatalf("GetDuration = %v", got)
	}
	if got := m.GetDuration("durnum"); got != 90*time.Second {
		t.Fatalf("GetDuration num = %v", got)
	}
}

func TestPaths(t *testing.T) {
	m := Of(map[string]interface{}{
		"profile": map[string]interface{}{
			"name": "Ada",
		},
		"users": []interface{}{
			map[string]interface{}{"name": "first"},
			map[string]interface{}{"name": "second"},
		},
	})

	if got := m.Path("profile.name"); got != "Ada" {
		t.Fatalf("Path = %v", got)
	}
	if got := m.Path("users[1].name"); got != "second" {
		t.Fatalf("Path bracket = %v", got)
	}
	if got := m.Path("users.0.name"); got != "first" {
		t.Fatalf("Path dotted index = %v", got)
	}
	if !m.HasPath("users[1].name") || m.HasPath("users[5].name") || m.HasPath("nope.x") {
		t.Fatal("HasPath mismatch")
	}
	if got := m.PathString("profile.name"); got != "Ada" {
		t.Fatalf("PathString = %q", got)
	}

	m.SetPath("profile.age", 36)
	if got := m.PathInt("profile.age"); got != 36 {
		t.Fatalf("SetPath = %v", got)
	}
	m.SetPath("a.b.c.d", "deep")
	if got := m.Path("a.b.c.d"); got != "deep" {
		t.Fatalf("SetPath deep = %v", got)
	}

	m.DeletePath("a.b.c.d")
	if m.HasPath("a.b.c.d") {
		t.Fatal("DeletePath failed")
	}
	m.DeletePath("profile.name")
	if m.HasPath("profile.name") {
		t.Fatal("DeletePath profile.name failed")
	}
}

func TestHasPathWithNilValue(t *testing.T) {
	m := Of(map[string]interface{}{"a": map[string]interface{}{"b": nil}})
	if !m.HasPath("a.b") {
		t.Fatal("HasPath should be true for a present nil value")
	}
	if m.Path("a.b") != nil {
		t.Fatal("Path should be nil")
	}
}

func TestJSON(t *testing.T) {
	m, err := FromJSONString(`{"name":"Ada","age":36,"tags":["x","y"]}`)
	if err != nil {
		t.Fatal(err)
	}
	if m.GetString("name") != "Ada" || m.GetInt("age") != 36 {
		t.Fatalf("FromJSONString = %v", m)
	}

	encoded, err := m.Encode()
	if err != nil {
		t.Fatal(err)
	}
	if encoded == "" {
		t.Fatal("Encode returned empty")
	}
	if got := m.String(); got != encoded {
		t.Fatalf("String = %q, want %q", got, encoded)
	}

	raw, err := m.ToJSON()
	if err != nil {
		t.Fatal(err)
	}
	var back map[string]interface{}
	if err := json.Unmarshal(raw, &back); err != nil {
		t.Fatal(err)
	}
	if back["name"] != "Ada" {
		t.Fatalf("ToJSON = %v", back)
	}
}

func TestJSONInterfaces(t *testing.T) {
	data, err := json.Marshal(Of(map[string]interface{}{"a": 1}))
	if err != nil {
		t.Fatal(err)
	}
	var m Map
	if err := json.Unmarshal(data, &m); err != nil {
		t.Fatal(err)
	}
	if m.GetInt("a") != 1 {
		t.Fatalf("UnmarshalJSON = %v", m)
	}

	nilJSON, err := json.Marshal(Map(nil))
	if err != nil {
		t.Fatal(err)
	}
	if string(nilJSON) != "null" {
		t.Fatalf("nil Map marshaled to %s", nilJSON)
	}

	if _, err := FromJSON([]byte("not json")); err == nil {
		t.Fatal("FromJSON should fail on invalid input")
	}
}

func TestStructConversion(t *testing.T) {
	type Profile struct {
		Name string `json:"name"`
		Age  int    `json:"age"`
	}
	m, err := FromStruct(Profile{Name: "Ada", Age: 36})
	if err != nil {
		t.Fatal(err)
	}
	if m.GetString("name") != "Ada" || m.GetInt("age") != 36 {
		t.Fatalf("FromStruct = %v", m)
	}

	var out Profile
	if err := m.Into(&out); err != nil {
		t.Fatal(err)
	}
	if out != (Profile{Name: "Ada", Age: 36}) {
		t.Fatalf("Into = %+v", out)
	}
}

func TestChaining(t *testing.T) {
	m := New().
		Set("id", 1).
		Set("password", "secret").
		Set("active", true).
		SetPath("profile.name", "Ada").
		Except("password").
		Clean()

	if m.Has("password") {
		t.Fatal("chained Except failed")
	}
	if !m.GetBool("active") || m.PathString("profile.name") != "Ada" {
		t.Fatalf("chained result = %v", m)
	}
}

package dynmap

import (
	"encoding/json"
	"reflect"
	"testing"
)

func TestSetAndGetNested(t *testing.T) {
	m := New().
		Set("user.name", "Ada").
		Set("user.age", 36).
		Set("user.address.city", "London")

	if got, ok := m.GetString("user.name"); !ok || got != "Ada" {
		t.Fatalf("GetString(user.name) = %q, %v; want Ada, true", got, ok)
	}
	if got, ok := m.GetInt("user.age"); !ok || got != 36 {
		t.Fatalf("GetInt(user.age) = %d, %v; want 36, true", got, ok)
	}
	if got, ok := m.GetString("user.address.city"); !ok || got != "London" {
		t.Fatalf("GetString(user.address.city) = %q, %v; want London, true", got, ok)
	}
	if m.Len() != 1 {
		t.Fatalf("Len() = %d; want 1", m.Len())
	}
}

func TestSetSliceIndex(t *testing.T) {
	m := New().Set("tags", []string{"a", "b"})
	m.Set("tags[1]", "c")
	m.Set("tags[3]", "d")

	got, ok := m.GetSlice("tags")
	if !ok {
		t.Fatal("GetSlice(tags) not found")
	}
	want := []interface{}{"a", "c", nil, "d"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("tags = %#v; want %#v", got, want)
	}
}

func TestSetRoot(t *testing.T) {
	m := New().Set("a", 1)
	m.Set("", map[string]interface{}{"b": 2})
	if m.Exists("a") {
		t.Fatal("root replacement should discard previous contents")
	}
	if got, _ := m.GetInt("b"); got != 2 {
		t.Fatalf("b = %d; want 2", got)
	}
}

func TestSetIndexAtRootIgnored(t *testing.T) {
	m := New().Set("a", 1)
	m.Set("[0]", "x")
	if m.Len() != 1 || !m.Exists("a") {
		t.Fatalf("Set with root index should be a no-op, got %v", m.Data())
	}
}

func TestGetMissing(t *testing.T) {
	m := Wrap(map[string]interface{}{"a": map[string]interface{}{"b": 1}})

	if _, ok := m.Get(""); !ok {
		t.Fatal(`Get("") should resolve to the root map`)
	}
	for _, path := range []string{"missing", "a.missing", "a.b.c", "a[0]", "a.b[0]"} {
		if _, ok := m.Get(path); ok {
			t.Fatalf("Get(%q) reported present", path)
		}
	}
}

func TestGetOrAndExists(t *testing.T) {
	m := New().Set("a", 1)
	if got := m.GetOr("a", 99); got != 1 {
		t.Fatalf("GetOr(a) = %v; want 1", got)
	}
	if got := m.GetOr("b", 99); got != 99 {
		t.Fatalf("GetOr(b) = %v; want 99", got)
	}
	if m.Exists("b") {
		t.Fatal("Exists(b) = true; want false")
	}
}

func TestSetIfAbsent(t *testing.T) {
	m := New().Set("a", 1).SetIfAbsent("a", 2).SetIfAbsent("b", 2)
	if got, _ := m.GetInt("a"); got != 1 {
		t.Fatalf("a = %d; want 1", got)
	}
	if got, _ := m.GetInt("b"); got != 2 {
		t.Fatalf("b = %d; want 2", got)
	}
}

func TestTypedGetters(t *testing.T) {
	m := Wrap(map[string]interface{}{
		"s":   "hello",
		"b":   true,
		"i":   42,
		"i6":  int64(7),
		"u":   uint(9),
		"f":   3.5,
		"n":   json.Number("12"),
		"bad": "not a number",
	})

	if got, ok := m.GetString("s"); !ok || got != "hello" {
		t.Fatalf("GetString = %q, %v", got, ok)
	}
	if got, ok := m.GetBool("b"); !ok || !got {
		t.Fatalf("GetBool = %v, %v", got, ok)
	}
	if got, ok := m.GetInt("i"); !ok || got != 42 {
		t.Fatalf("GetInt = %d, %v", got, ok)
	}
	if got, ok := m.GetInt64("i6"); !ok || got != 7 {
		t.Fatalf("GetInt64 = %d, %v", got, ok)
	}
	if got, ok := m.GetInt("u"); !ok || got != 9 {
		t.Fatalf("GetInt(uint) = %d, %v", got, ok)
	}
	if got, ok := m.GetInt("f"); !ok || got != 3 {
		t.Fatalf("GetInt(3.5) = %d, %v; want truncated 3", got, ok)
	}
	if got, ok := m.GetFloat64("f"); !ok || got != 3.5 {
		t.Fatalf("GetFloat64 = %v, %v", got, ok)
	}
	if got, ok := m.GetInt("n"); !ok || got != 12 {
		t.Fatalf("GetInt(json.Number) = %d, %v", got, ok)
	}
	if _, ok := m.GetInt("bad"); ok {
		t.Fatal("GetInt on string should fail")
	}
	if _, ok := m.GetString("bad"); !ok {
		t.Fatal("GetString on string should succeed")
	}
}

func TestGetSliceReflection(t *testing.T) {
	m := Wrap(map[string]interface{}{"tags": []string{"a", "b"}, "nums": [3]int{1, 2, 3}})
	if got, ok := m.GetSlice("tags"); !ok || !reflect.DeepEqual(got, []interface{}{"a", "b"}) {
		t.Fatalf("GetSlice(tags) = %#v, %v", got, ok)
	}
	if got, ok := m.GetSlice("nums"); !ok || !reflect.DeepEqual(got, []interface{}{1, 2, 3}) {
		t.Fatalf("GetSlice(nums) = %#v, %v", got, ok)
	}
	if _, ok := m.GetSlice("tags[0]"); ok {
		t.Fatal("GetSlice of scalar should fail")
	}
}

func TestSubAndEnsureMap(t *testing.T) {
	m := New().Set("user.name", "Ada")
	sub := m.Sub("user")
	if sub == nil {
		t.Fatal("Sub(user) returned nil")
	}
	sub.Set("age", 36)
	if got, _ := m.GetInt("user.age"); got != 36 {
		t.Fatalf("Sub did not alias the parent map: age = %d", got)
	}
	if m.Sub("missing") != nil {
		t.Fatal("Sub(missing) should be nil")
	}

	created := m.EnsureMap("a.b.c")
	created.Set("ok", true)
	if got, _ := m.GetBool("a.b.c.ok"); !got {
		t.Fatal("EnsureMap did not attach the created nested map")
	}
}

func TestDelete(t *testing.T) {
	m := New().
		Set("user.name", "Ada").
		Set("user.age", 36).
		Set("xs", []interface{}{1, 2, 3})

	m.Delete("user.age")
	if m.Exists("user.age") {
		t.Fatal("Delete(user.age) left the value present")
	}
	if !m.Exists("user.name") {
		t.Fatal("Delete removed a sibling")
	}

	m.Delete("xs[1]")
	if got, _ := m.GetSlice("xs"); !reflect.DeepEqual(got, []interface{}{1, 3}) {
		t.Fatalf("xs after delete = %#v; want [1 3]", got)
	}

	m.Delete("missing")
	m.Delete("")
}

func TestMergeShallow(t *testing.T) {
	m := New().
		Set("a", map[string]interface{}{"x": 1, "y": 2}).
		Set("keep", true)
	m.Merge(map[string]interface{}{"a": map[string]interface{}{"z": 9}, "new": 1})

	if got, _ := m.GetMap("a"); !reflect.DeepEqual(got, map[string]interface{}{"z": 9}) {
		t.Fatalf("Merge should replace nested maps, got %#v", got)
	}
	if got, _ := m.GetBool("keep"); !got {
		t.Fatal("Merge dropped an existing unrelated key")
	}
}

func TestMergeDeep(t *testing.T) {
	m := New().Set("a", map[string]interface{}{"x": 1, "y": 2})
	m.MergeDeep(map[string]interface{}{"a": map[string]interface{}{"y": 3, "z": 4}})

	want := map[string]interface{}{"x": 1, "y": 3, "z": 4}
	if got, _ := m.GetMap("a"); !reflect.DeepEqual(got, want) {
		t.Fatalf("MergeDeep = %#v; want %#v", got, want)
	}
}

func TestAppend(t *testing.T) {
	m := New().Append("xs", 1, 2).Append("xs", 3)
	if got, _ := m.GetSlice("xs"); !reflect.DeepEqual(got, []interface{}{1, 2, 3}) {
		t.Fatalf("xs = %#v; want [1 2 3]", got)
	}
}

func TestClone(t *testing.T) {
	m := New().Set("a.b", 1).Set("xs", []interface{}{1, 2})
	c := m.Clone()
	c.Set("a.b", 2)
	c.Set("xs[0]", 99)

	if got, _ := m.GetInt("a.b"); got != 1 {
		t.Fatalf("Clone mutated the original: a.b = %d", got)
	}
	if got, _ := m.GetSlice("xs"); !reflect.DeepEqual(got, []interface{}{1, 2}) {
		t.Fatalf("Clone mutated the original slice: xs = %#v", got)
	}
}

func TestKeysLen(t *testing.T) {
	m := New().Set("b", 1).Set("a", 2)
	if m.Len() != 2 {
		t.Fatalf("Len() = %d; want 2", m.Len())
	}
	if got := m.Keys(); !reflect.DeepEqual(got, []string{"a", "b"}) {
		t.Fatalf("Keys() = %#v; want [a b]", got)
	}
}

func TestWrapNil(t *testing.T) {
	m := Wrap(nil)
	if m.Len() != 0 {
		t.Fatalf("Wrap(nil).Len() = %d; want 0", m.Len())
	}
	m.Set("a", 1)
	if got, _ := m.GetInt("a"); got != 1 {
		t.Fatalf("a = %d; want 1", got)
	}
}

func TestJSON(t *testing.T) {
	m := New().Set("a", 1).Set("b.c", "x")
	if got, want := m.String(), `{"a":1,"b":{"c":"x"}}`; got != want {
		t.Fatalf("String() = %s; want %s", got, want)
	}

	b, err := json.Marshal(m)
	if err != nil {
		t.Fatalf("json.Marshal: %v", err)
	}
	if string(b) != m.String() {
		t.Fatalf("json.Marshal = %s; want %s", b, m.String())
	}

	parsed, err := Parse([]byte(`{"n":1.5,"s":"hi"}`))
	if err != nil {
		t.Fatalf("Parse: %v", err)
	}
	if got, ok := parsed.GetFloat64("n"); !ok || got != 1.5 {
		t.Fatalf("parsed n = %v, %v", got, ok)
	}

	empty := New()
	if err := empty.UnmarshalJSON([]byte(`null`)); err != nil {
		t.Fatalf("UnmarshalJSON(null): %v", err)
	}
	if empty.Len() != 0 {
		t.Fatalf("UnmarshalJSON(null) left %d keys", empty.Len())
	}

	if err := New().UnmarshalJSON([]byte(`not json`)); err == nil {
		t.Fatal("UnmarshalJSON(invalid) = nil; want error")
	}
}

func TestWrapAliasesData(t *testing.T) {
	raw := map[string]interface{}{"a": 1}
	m := Wrap(raw)
	m.Set("b", 2)
	if _, ok := raw["b"]; !ok {
		t.Fatal("Wrap should alias the provided map")
	}
}

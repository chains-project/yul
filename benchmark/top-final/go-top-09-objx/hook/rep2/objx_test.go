package objx

import "testing"

func TestConstructors(t *testing.T) {
	m := New(map[string]interface{}{"a": 1})
	if m.Get("a").Int() != 1 {
		t.Fatalf("New: got %v", m.Get("a").Data())
	}

	m2 := MSI("name", "Mat", "age", 30)
	if m2.Get("name").Str() != "Mat" || m2.Get("age").Int() != 30 {
		t.Fatalf("MSI: got %#v", m2)
	}

	m3, err := FromJSON(`{"a":{"b":"c"}}`)
	if err != nil {
		t.Fatalf("FromJSON error: %v", err)
	}
	if m3.Get("a.b").Str() != "c" {
		t.Fatalf("FromJSON: got %v", m3.Get("a.b").Data())
	}

	if _, err := FromJSON(`not json`); err == nil {
		t.Fatalf("expected error for invalid json")
	}
}

func TestGetDottedAndIndexed(t *testing.T) {
	m := MustFromJSON(`{
		"name": "Mat",
		"age": 30,
		"friends": [
			{"name": "Tyler"},
			{"name": "Capitol"}
		],
		"address": {"city": "London"}
	}`)

	if m.Get("address.city").Str() != "London" {
		t.Fatalf("got %v", m.Get("address.city").Data())
	}
	if m.Get("friends[0].name").Str() != "Tyler" {
		t.Fatalf("got %v", m.Get("friends[0].name").Data())
	}
	if m.Get("friends[1].name").Str() != "Capitol" {
		t.Fatalf("got %v", m.Get("friends[1].name").Data())
	}
	if !m.Get("friends[5].name").IsNil() {
		t.Fatalf("expected nil for out-of-range index")
	}
	if !m.Get("nope.nope").IsNil() {
		t.Fatalf("expected nil for missing path")
	}
}

func TestValueDefaultsAndTypes(t *testing.T) {
	m := MSI("str", "hello", "n", 42, "f", 3.14, "b", true)

	if got := m.Get("missing").Str("fallback"); got != "fallback" {
		t.Fatalf("got %v", got)
	}
	if got := m.Get("missing").Int(7); got != 7 {
		t.Fatalf("got %v", got)
	}
	if got := m.Get("missing").Bool(true); got != true {
		t.Fatalf("got %v", got)
	}

	if !m.Get("str").IsStr() || m.Get("str").MustStr() != "hello" {
		t.Fatalf("string accessors failed")
	}
	if !m.Get("n").IsNumeric() || m.Get("n").Int() != 42 {
		t.Fatalf("int accessors failed")
	}
	if m.Get("f").Float64() != 3.14 {
		t.Fatalf("float accessor failed")
	}
	if !m.Get("b").IsBool() || !m.Get("b").Bool() {
		t.Fatalf("bool accessors failed")
	}
}

func TestValueMustStrPanics(t *testing.T) {
	defer func() {
		if recover() == nil {
			t.Fatalf("expected panic")
		}
	}()
	MSI("n", 1).Get("n").MustStr()
}

func TestValueChainedGet(t *testing.T) {
	m := MustFromJSON(`{"a":{"b":{"c":"deep"}}}`)
	v := m.Get("a").Get("b").Get("c")
	if v.Str() != "deep" {
		t.Fatalf("got %v", v.Data())
	}
}

func TestValueSliceAccessors(t *testing.T) {
	m := MustFromJSON(`{"tags": ["a", "b", "c"], "mixed": ["a", 1, "b"]}`)
	if got := m.Get("tags").StrSlice(); len(got) != 3 || got[0] != "a" {
		t.Fatalf("got %#v", got)
	}
	if got := m.Get("mixed").StrSlice(); len(got) != 2 {
		t.Fatalf("expected non-strings filtered out, got %#v", got)
	}
	if !m.Get("tags").IsSlice() {
		t.Fatalf("expected slice")
	}
}

func TestSet(t *testing.T) {
	m := Map{}
	m.Set("a.b.c", "value")
	if m.Get("a.b.c").Str() != "value" {
		t.Fatalf("got %v", m.Get("a.b.c").Data())
	}

	// Overwriting an existing scalar with a nested path replaces it with a map.
	m2 := MSI("a", "scalar")
	m2.Set("a.b", "value")
	if m2.Get("a.b").Str() != "value" {
		t.Fatalf("got %v", m2.Get("a.b").Data())
	}

	// Chainable.
	m3 := Map{}
	result := m3.Set("x", 1)
	if result.Get("x").Int() != 1 {
		t.Fatalf("Set should return receiver")
	}
}

func TestHasAndKeys(t *testing.T) {
	m := MSI("a", 1, "b", 2)
	if !m.Has("a") || m.Has("z") {
		t.Fatalf("Has failed")
	}
	keys := m.Keys()
	if len(keys) != 2 {
		t.Fatalf("got %v", keys)
	}
}

func TestCopyIsIndependent(t *testing.T) {
	m := MSI("a", 1)
	c := m.Copy()
	c.Set("a", 2)
	if m.Get("a").Int() != 1 {
		t.Fatalf("Copy should be independent, original mutated: %v", m.Get("a").Data())
	}
}

func TestMerge(t *testing.T) {
	m := MSI("a", 1, "b", 2)
	other := MSI("b", 20, "c", 3)

	merged := m.Merge(other)
	if merged.Get("a").Int() != 1 || merged.Get("b").Int() != 20 || merged.Get("c").Int() != 3 {
		t.Fatalf("got %#v", merged)
	}
	if m.Get("b").Int() != 2 {
		t.Fatalf("Merge should not mutate original, got %v", m.Get("b").Data())
	}

	m.MergeHere(other)
	if m.Get("b").Int() != 20 || m.Get("c").Int() != 3 {
		t.Fatalf("MergeHere should mutate in place, got %#v", m)
	}
}

func TestExcludeAndInclude(t *testing.T) {
	m := MSI("a", 1, "b", 2, "c", 3)

	excluded := m.Exclude([]string{"b"})
	if excluded.Has("b") || !excluded.Has("a") || !excluded.Has("c") {
		t.Fatalf("got %#v", excluded)
	}
	if len(m) != 3 {
		t.Fatalf("Exclude should not mutate original")
	}

	included := m.Include([]string{"a", "c", "nonexistent"})
	if len(included) != 2 || !included.Has("a") || !included.Has("c") {
		t.Fatalf("got %#v", included)
	}
}

func TestMapAccessorAndJSON(t *testing.T) {
	m := MustFromJSON(`{"nested":{"k":"v"}}`)
	nested := m.Get("nested").Map()
	if nested.Get("k").Str() != "v" {
		t.Fatalf("got %#v", nested)
	}
	if !m.Get("nested").IsMap() {
		t.Fatalf("expected IsMap true")
	}

	j, err := m.JSON()
	if err != nil || j == "" {
		t.Fatalf("JSON() failed: %v", err)
	}
	roundtrip := MustFromJSON(j)
	if roundtrip.Get("nested.k").Str() != "v" {
		t.Fatalf("roundtrip failed: %#v", roundtrip)
	}
}

func TestMSIPanicsOnOddArgs(t *testing.T) {
	defer func() {
		if recover() == nil {
			t.Fatalf("expected panic")
		}
	}()
	MSI("a")
}

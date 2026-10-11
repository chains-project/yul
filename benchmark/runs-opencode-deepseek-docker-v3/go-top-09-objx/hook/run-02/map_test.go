package mapx

import (
	"reflect"
	"testing"
)

func TestGetNestedAndIndex(t *testing.T) {
	m := New(map[string]interface{}{
		"user": map[string]interface{}{
			"name": "ada",
			"tags": []interface{}{"math", "code"},
		},
		"list": []interface{}{
			map[string]interface{}{"id": float64(7)},
		},
	})

	if got := m.Get("user.name").String(); got != "ada" {
		t.Fatalf("got %q", got)
	}
	if got := m.Get("user.tags[1]").String(); got != "code" {
		t.Fatalf("got %q", got)
	}
	if got := m.Get("list.0.id").Int(); got != 7 {
		t.Fatalf("got %d", got)
	}
	if v := m.Get("user.missing"); v.Exists() {
		t.Fatalf("expected missing")
	}
	if !m.Has("user.tags[0]") {
		t.Fatalf("expected has")
	}
}

func TestSetCreatesPath(t *testing.T) {
	m := New(nil)
	m.Set("a.b.c", 1).Set("a.b.d", 2).Set("items[]", "x").Set("items[]", "y")
	if got := m.Get("a.b.c").Int(); got != 1 {
		t.Fatalf("c = %d", got)
	}
	if got := m.Get("a.b.d").Int(); got != 2 {
		t.Fatalf("d = %d", got)
	}
	want := []interface{}{"x", "y"}
	if got := m.Get("items").Slice(); !reflect.DeepEqual(got, want) {
		t.Fatalf("items = %#v", got)
	}
}

func TestSetSliceIndexAndGrow(t *testing.T) {
	m := New(map[string]interface{}{"a": []interface{}{1, 2}})
	m.Set("a[1]", 9).Set("a[3]", 4)
	if got := m.Get("a").Slice(); !reflect.DeepEqual(got, []interface{}{1, 9, nil, 4}) {
		t.Fatalf("a = %#v", got)
	}
}

func TestDelete(t *testing.T) {
	m := New(map[string]interface{}{
		"a": map[string]interface{}{"b": 1, "c": 2},
		"l": []interface{}{"x", "y", "z"},
	})
	m.Delete("a.b").Delete("l[1]")
	if m.Has("a.b") {
		t.Fatalf("a.b should be gone")
	}
	if got := m.Get("a.c").Int(); got != 2 {
		t.Fatalf("a.c = %d", got)
	}
	if got := m.Get("l").Slice(); !reflect.DeepEqual(got, []interface{}{"x", "z"}) {
		t.Fatalf("l = %#v", got)
	}
}

func TestMergeDeep(t *testing.T) {
	a := New(map[string]interface{}{
		"x": map[string]interface{}{"a": 1, "b": 2},
		"y": 1,
	})
	b := New(map[string]interface{}{
		"x": map[string]interface{}{"b": 3, "c": 4},
		"z": 5,
	})
	a.Merge(b)
	if got := a.Get("x.a").Int(); got != 1 {
		t.Fatalf("x.a = %d", got)
	}
	if got := a.Get("x.b").Int(); got != 3 {
		t.Fatalf("x.b = %d", got)
	}
	if got := a.Get("x.c").Int(); got != 4 {
		t.Fatalf("x.c = %d", got)
	}
	if got := a.Get("z").Int(); got != 5 {
		t.Fatalf("z = %d", got)
	}
}

func TestCloneIsDeep(t *testing.T) {
	src := New(map[string]interface{}{"a": map[string]interface{}{"b": 1}})
	cp := src.Clone()
	cp.Set("a.b", 2)
	if got := src.Get("a.b").Int(); got != 1 {
		t.Fatalf("src a.b = %d", got)
	}
	if got := cp.Get("a.b").Int(); got != 2 {
		t.Fatalf("cp a.b = %d", got)
	}
}

func TestFilterAndKeys(t *testing.T) {
	m := New(map[string]interface{}{"a": 1, "b": 2, "c": 3})
	got := m.Filter(func(_ string, v *Value) bool { return v.Int() > 1 })
	if !reflect.DeepEqual(got.Keys(), []string{"b", "c"}) {
		t.Fatalf("keys = %v", got.Keys())
	}
	if !reflect.DeepEqual(m.Keys(), []string{"a", "b", "c"}) {
		t.Fatalf("keys = %v", m.Keys())
	}
}

func TestValueConversions(t *testing.T) {
	m := New(map[string]interface{}{
		"n":   "42",
		"f":   float64(3.5),
		"b":   "true",
		"arr": []interface{}{1, true, "x"},
	})
	if got := m.Get("n").Int(); got != 42 {
		t.Fatalf("n = %d", got)
	}
	if got := m.Get("f").Float(); got != 3.5 {
		t.Fatalf("f = %v", got)
	}
	if got := m.Get("b").Bool(); !got {
		t.Fatalf("b = %v", got)
	}
	if got := m.Get("missing").IntOr(9); got != 9 {
		t.Fatalf("missing = %d", got)
	}
	if got := m.Get("missing").StringOr("def"); got != "def" {
		t.Fatalf("missing = %q", got)
	}
	want := []string{"1", "true", "x"}
	if got := m.Get("arr").Strings(); !reflect.DeepEqual(got, want) {
		t.Fatalf("arr = %#v", got)
	}
}

func TestJSONRoundTrip(t *testing.T) {
	m, err := FromJSON([]byte(`{"a":{"b":[1,2,{"c":true}]}}`))
	if err != nil {
		t.Fatal(err)
	}
	if !m.Get("a.b[2].c").Bool() {
		t.Fatalf("unexpected: %s", m)
	}
	b, err := m.MarshalJSON()
	if err != nil {
		t.Fatal(err)
	}
	again, err := FromJSON(b)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(m.Data(), again.Data()) {
		t.Fatalf("round trip mismatch: %s vs %s", m, again)
	}
}

func TestEach(t *testing.T) {
	m := New(map[string]interface{}{"a": 1, "b": 2})
	sum := 0
	seen := m.Each(func(_ string, v *Value) { sum += v.Int() })
	if seen != m || sum != 3 {
		t.Fatalf("sum = %d", sum)
	}
}

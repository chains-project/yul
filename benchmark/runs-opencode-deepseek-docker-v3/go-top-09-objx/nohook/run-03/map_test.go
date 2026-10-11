package chainmap

import (
	"errors"
	"testing"
)

func sample() *Map {
	return New(map[string]interface{}{
		"name":  "ada",
		"age":   float64(36),
		"admin": true,
		"tags":  []interface{}{"go", "math"},
		"user": map[string]interface{}{
			"profile": map[string]interface{}{
				"city": "london",
			},
		},
	})
}

func TestGetAndCoercion(t *testing.T) {
	m := sample()

	if got := m.Get("name").String(); got != "ada" {
		t.Fatalf("String() = %q, want ada", got)
	}
	if got := m.Get("age").Int(); got != 36 {
		t.Fatalf("Int() = %d, want 36", got)
	}
	if got := m.Get("age").Float64(); got != 36 {
		t.Fatalf("Float64() = %v, want 36", got)
	}
	if got := m.Get("admin").Bool(); got != true {
		t.Fatalf("Bool() = %v, want true", got)
	}
	if err := m.Err(); err != nil {
		t.Fatalf("unexpected chain error: %v", err)
	}
}

func TestMissingKeyRecordsNotFound(t *testing.T) {
	m := sample()
	v := m.Get("missing")
	if !errors.Is(v.Err(), ErrNotFound) {
		t.Fatalf("Err() = %v, want ErrNotFound", v.Err())
	}
	if v.Exists() {
		t.Fatal("Exists() = true, want false")
	}
}

func TestTypeMismatchRecordsError(t *testing.T) {
	m := sample()
	v := m.Get("name")
	if got := v.Int(); got != 0 {
		t.Fatalf("Int() = %d, want 0", got)
	}
	if !errors.Is(v.Err(), ErrTypeMismatch) {
		t.Fatalf("Err() = %v, want ErrTypeMismatch", v.Err())
	}
}

func TestOrVariantsDoNotError(t *testing.T) {
	m := sample()
	if got := m.Get("missing").StringOr("fallback"); got != "fallback" {
		t.Fatalf("StringOr = %q, want fallback", got)
	}
	if got := m.Get("name").IntOr(7); got != 7 {
		t.Fatalf("IntOr = %d, want 7", got)
	}
	if got := m.Get("age").Int64Or(-1); got != 36 {
		t.Fatalf("Int64Or = %d, want 36", got)
	}
	if got := m.Get("name").BoolOr(true); got != true {
		t.Fatalf("BoolOr = %v, want true", got)
	}
	if got := m.Get("missing").Float64Or(1.5); got != 1.5 {
		t.Fatalf("Float64Or = %v, want 1.5", got)
	}
}

func TestPathTraversal(t *testing.T) {
	m := sample()
	if got := m.Path("user.profile.city").String(); got != "london" {
		t.Fatalf("Path = %q, want london", got)
	}
	if got := m.Path("tags.1").String(); got != "math" {
		t.Fatalf("Path = %q, want math", got)
	}
	if !errors.Is(m.Path("tags.9").Err(), ErrIndexOutOfRange) {
		t.Fatalf("Err() = %v, want ErrIndexOutOfRange", m.Path("tags.9").Err())
	}
	if !errors.Is(m.Path("user.nope.city").Err(), ErrNotFound) {
		t.Fatalf("Err() = %v, want ErrNotFound", m.Path("user.nope.city").Err())
	}
}

func TestSetAndDelete(t *testing.T) {
	m := sample()
	m.Set("name", "grace").Set("active", true).Delete("age")

	if m.Get("name").String() != "grace" {
		t.Fatal("Set did not update name")
	}
	if !m.Get("active").Bool() {
		t.Fatal("Set did not add active")
	}
	if m.Has("age") {
		t.Fatal("Delete did not remove age")
	}
}

func TestSetPathCreatesIntermediateMaps(t *testing.T) {
	m := New(nil)
	m.SetPath("a.b.c", 42)
	if got := m.Path("a.b.c").Int(); got != 42 {
		t.Fatalf("SetPath value = %d, want 42", got)
	}

	bad := New(map[string]interface{}{"a": "not-a-map"})
	bad.SetPath("a.b", 1)
	if !errors.Is(bad.Err(), ErrTypeMismatch) {
		t.Fatalf("Err() = %v, want ErrTypeMismatch", bad.Err())
	}
}

func TestDeletePath(t *testing.T) {
	m := sample()
	m.DeletePath("user.profile.city")
	if m.Path("user.profile.city").Err() == nil {
		t.Fatal("DeletePath did not remove value")
	}
}

func TestSliceOperations(t *testing.T) {
	s := NewSlice([]interface{}{1, 2, 3})
	s.Append(4).Prepend(0)

	want := []int{0, 1, 2, 3, 4}
	got := s.Values()
	if len(got) != len(want) {
		t.Fatalf("len = %d, want %d", len(got), len(want))
	}
	for i, w := range want {
		if v := got[i].Int(); v != w {
			t.Fatalf("index %d = %d, want %d", i, v, w)
		}
	}

	doubled := NewSlice([]interface{}{1, 2, 3}).Transform(func(_ int, v *Value) interface{} {
		return v.Int() * 2
	})
	if doubled.Index(2).Int() != 6 {
		t.Fatalf("Transform = %d, want 6", doubled.Index(2).Int())
	}

	evens := NewSlice([]interface{}{1, 2, 3, 4}).Filter(func(_ int, v *Value) bool {
		return v.Int()%2 == 0
	})
	if evens.Len() != 2 || evens.Index(0).Int() != 2 || evens.Index(1).Int() != 4 {
		t.Fatalf("Filter produced %v", evens.Raw())
	}
}

func TestValueSliceAndMap(t *testing.T) {
	m := sample()
	tags := m.Get("tags").Slice()
	if tags.Len() != 2 {
		t.Fatalf("tags len = %d, want 2", tags.Len())
	}
	if tags.Index(0).String() != "go" {
		t.Fatalf("tags[0] = %q, want go", tags.Index(0).String())
	}

	if _, ok := m.Get("user").Map().Get("profile").Map().Raw()["city"]; !ok {
		t.Fatal("nested Map access failed")
	}
}

func TestEachAndTransform(t *testing.T) {
	sum := 0
	New(map[string]interface{}{"a": 1, "b": 2, "c": 3}).
		Each(func(_ string, v *Value) bool { sum += v.Int(); return true })
	if sum != 6 {
		t.Fatalf("Each sum = %d, want 6", sum)
	}

	m := New(map[string]interface{}{"a": 1, "b": 2})
	m.Transform(func(_ string, v *Value) interface{} { return v.Int() * 10 })
	if m.Get("a").Int() != 10 || m.Get("b").Int() != 20 {
		t.Fatalf("Transform result = %v", m.Raw())
	}
}

func TestMergeAndClone(t *testing.T) {
	base := New(map[string]interface{}{"a": 1, "nested": map[string]interface{}{"x": 1}})
	base.Merge(New(map[string]interface{}{"b": 2}))
	if base.Len() != 3 {
		t.Fatalf("Len = %d, want 3", base.Len())
	}

	clone := base.Clone()
	clone.SetPath("nested.x", 99)
	if base.Path("nested.x").Int() != 1 {
		t.Fatal("Clone shares nested maps with the original")
	}
}

func TestParseJSON(t *testing.T) {
	m, err := ParseJSON([]byte(`{"user":{"name":"ada","age":36},"tags":["a","b"]}`))
	if err != nil {
		t.Fatalf("ParseJSON: %v", err)
	}
	if m.Path("user.name").String() != "ada" {
		t.Fatalf("name = %q, want ada", m.Path("user.name").String())
	}
	if m.Path("user.age").Int() != 36 {
		t.Fatalf("age = %d, want 36", m.Path("user.age").Int())
	}
	if m.Path("tags.1").String() != "b" {
		t.Fatalf("tags[1] = %q, want b", m.Path("tags.1").String())
	}
}

func TestErrorPropagationThroughChain(t *testing.T) {
	m := sample()
	v := m.Path("user.missing.city")
	if !errors.Is(v.Err(), ErrNotFound) {
		t.Fatalf("Err() = %v, want ErrNotFound", v.Err())
	}
	// Subsequent reads after an error stay in the error state.
	if v.Get("anything").Err() == nil {
		t.Fatal("error was not propagated")
	}
}

func TestEmptyKeyLookup(t *testing.T) {
	m := New(map[string]interface{}{"": "blank"})
	if got := m.Get("").String(); got != "blank" {
		t.Fatalf("Get(\"\") = %q, want blank", got)
	}
}

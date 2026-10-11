package mapx

import (
	"encoding/json"
	"errors"
	"reflect"
	"testing"
)

func TestSetAndGetNested(t *testing.T) {
	w := New(nil).
		Set("user.name", "Ada").
		Set("user.age", 36).
		Set("user.tags[0]", "admin").
		Set("user.tags[1]", "dev")

	if err := w.Err(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got := w.Get("user.name").String(); got != "Ada" {
		t.Errorf("name = %q, want Ada", got)
	}
	if got := w.Get("user.age").Int(); got != 36 {
		t.Errorf("age = %d, want 36", got)
	}
	if got := w.Get("user.tags[1]").String(); got != "dev" {
		t.Errorf("tags[1] = %q, want dev", got)
	}
}

func TestSetCreatesIntermediateContainers(t *testing.T) {
	w := New(nil).Set("a[0].b.c", "deep")
	if got := w.Get("a[0].b.c").String(); got != "deep" {
		t.Fatalf("got %q", got)
	}
	sl := w.Get("a").Slice()
	if len(sl) != 1 {
		t.Fatalf("a len = %d, want 1", len(sl))
	}
}

func TestGetMissingAndTypeErrors(t *testing.T) {
	w := New(map[string]interface{}{"n": 5})

	missing := w.Get("nope")
	if !errors.Is(missing.Err(), ErrNotFound) {
		t.Errorf("err = %v, want ErrNotFound", missing.Err())
	}
	if missing.Exists() {
		t.Error("missing should not exist")
	}

	bad := w.Get("n").String()
	_ = bad
	// string conversion never fails, but navigating a non-map does
	if err := w.Get("n.child").Err(); !errors.Is(err, ErrTypeMismatch) {
		t.Errorf("err = %v, want ErrTypeMismatch", err)
	}
}

func TestPathErrors(t *testing.T) {
	for _, p := range []string{"", "a..b", "a.", "a[", "a[x]"} {
		if !errors.Is(parseErr(p), ErrInvalidPath) {
			t.Errorf("path %q: got %v, want ErrInvalidPath", p, parseErr(p))
		}
	}
}

func parseErr(p string) error {
	return New(nil).Get(p).Err()
}

func TestDelete(t *testing.T) {
	w := New(map[string]interface{}{"a": map[string]interface{}{"b": 1, "c": 2}})
	w.Delete("a.b")
	if w.Has("a.b") {
		t.Error("a.b should be deleted")
	}
	if !w.Has("a.c") {
		t.Error("a.c should remain")
	}
	if err := w.Delete("a.missing").Err(); !errors.Is(err, ErrNotFound) {
		t.Errorf("err = %v, want ErrNotFound", err)
	}
}

func TestKeysAndLen(t *testing.T) {
	w := New(map[string]interface{}{"c": 1, "a": 2, "b": 3})
	if w.Len() != 3 {
		t.Errorf("len = %d, want 3", w.Len())
	}
	want := []string{"a", "b", "c"}
	if got := w.Keys(); !reflect.DeepEqual(got, want) {
		t.Errorf("keys = %v, want %v", got, want)
	}
}

func TestMerge(t *testing.T) {
	w := New(map[string]interface{}{"a": 1}).Merge(map[string]interface{}{"b": 2, "a": 9})
	if got := w.Get("a").Int(); got != 9 {
		t.Errorf("a = %d, want 9", got)
	}
	if got := w.Get("b").Int(); got != 2 {
		t.Errorf("b = %d, want 2", got)
	}
}

func TestCloneIsDeep(t *testing.T) {
	original := New(map[string]interface{}{"nested": map[string]interface{}{"x": 1}})
	clone := original.Clone().Set("nested.x", 2)

	if got := original.Get("nested.x").Int(); got != 1 {
		t.Errorf("original changed to %d, want 1", got)
	}
	if got := clone.Get("nested.x").Int(); got != 2 {
		t.Errorf("clone = %d, want 2", got)
	}
}

func TestValueConversions(t *testing.T) {
	w := New(map[string]interface{}{
		"intStr":    "42",
		"float":     3.9,
		"boolStr":   "true",
		"num":       json.Number("7"),
		"boolNum":   1,
		"list":      []interface{}{"a", "b"},
		"nested":    map[string]interface{}{"k": "v"},
		"byteSlice": []byte("hi"),
	})

	if got := w.Get("intStr").Int(); got != 42 {
		t.Errorf("intStr = %d", got)
	}
	if got := w.Get("float").Int(); got != 3 {
		t.Errorf("float = %d", got)
	}
	if got := w.Get("num").Int64(); got != 7 {
		t.Errorf("num = %d", got)
	}
	if !w.Get("boolStr").Bool() {
		t.Error("boolStr should be true")
	}
	if !w.Get("boolNum").Bool() {
		t.Error("boolNum should be true")
	}
	if got := w.Get("list").Slice(); len(got) != 2 {
		t.Errorf("list len = %d", len(got))
	}
	if got := w.Get("nested").Get("k").String(); got != "v" {
		t.Errorf("nested.k = %q", got)
	}
	if got := w.Get("byteSlice").String(); got != "hi" {
		t.Errorf("byteSlice = %q", got)
	}
}

func TestOrFallback(t *testing.T) {
	w := New(nil)
	if got := w.Get("missing").Or("default").String(); got != "default" {
		t.Errorf("got %q, want default", got)
	}
	if got := w.Get("missing").Get("deeper").Or(5).Int(); got != 5 {
		t.Errorf("got %d, want 5", got)
	}
}

func TestNamedMapInput(t *testing.T) {
	m := Map{"a": Map{"b": 1}}
	w := New(map[string]interface{}(m))
	if got := w.Get("a.b").Int(); got != 1 {
		t.Errorf("a.b = %d, want 1", got)
	}
	w.Set("a.c", 2)
	if got := m["a"].(Map)["c"]; got != 2 {
		t.Errorf("named map not mutated: %v", got)
	}
}

func TestDeleteSliceSetsNil(t *testing.T) {
	w := New(nil).Set("xs[0]", "a").Set("xs[1]", "b")
	w.Delete("xs[0]")
	if w.Get("xs[0]").Raw() != nil {
		t.Error("xs[0] should be nil")
	}
	if got := w.Get("xs[1]").String(); got != "b" {
		t.Errorf("xs[1] = %q, want b", got)
	}
}

func TestConversionErrors(t *testing.T) {
	w := New(map[string]interface{}{"s": "nope", "n": 1, "b": false})

	if got := w.Get("s").Int(); got != 0 {
		t.Errorf("string int = %d, want 0", got)
	}
	v := w.Get("s")
	v.Int64()
	if !errors.Is(v.Err(), ErrTypeMismatch) {
		t.Errorf("Int64 err = %v", v.Err())
	}
	if got := w.Get("s").Bool(); got {
		t.Error("string bool should be false")
	}
	if gow := w.Get("s").Float64(); gow != 0 {
		t.Errorf("float = %v", gow)
	}
	if m := w.Get("n").Map(); m != nil {
		t.Errorf("map = %v, want nil", m)
	}
	if s := w.Get("n").Slice(); s != nil {
		t.Errorf("slice = %v, want nil", s)
	}
	if !w.Get("b").IsNil() == false {
		t.Error("IsNil should be false")
	}
	if got := w.Get("n").Float64(); got != 1 {
		t.Errorf("float = %v, want 1", got)
	}
}

func TestSetErrorSticksAndShortCircuits(t *testing.T) {
	w := New(map[string]interface{}{"a": "scalar"})
	w.Set("a.b", 1)
	if w.Err() == nil {
		t.Fatal("expected error")
	}
	// subsequent Set is a no-op and error is preserved
	w.Set("c", 2)
	if w.Has("c") {
		t.Error("c should not be set after error")
	}
}

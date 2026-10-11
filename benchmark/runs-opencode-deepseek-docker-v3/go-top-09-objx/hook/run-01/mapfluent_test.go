package mapfluent

import (
	"reflect"
	"testing"
)

func TestSetGetNested(t *testing.T) {
	m := New().
		Set("user.name", "Ada").
		Set("user.address.city", "London").
		Set("user.age", 36)

	if got := m.Get("user.name"); got != "Ada" {
		t.Fatalf("Get user.name = %v", got)
	}
	if got := m.Get("user.address.city"); got != "London" {
		t.Fatalf("Get nested = %v", got)
	}
	if got := m.String("user.name", ""); got != "Ada" {
		t.Fatalf("String = %q", got)
	}
	if got := m.Int("user.age"); got != 36 {
		t.Fatalf("Int = %d", got)
	}
}

func TestPathForms(t *testing.T) {
	m := New().Set("a.b[0].c", 1).Set("a.b[2].c", 3)

	if got := m.Int("$.a.b[0].c"); got != 1 {
		t.Fatalf("dollar path = %d", got)
	}
	if got := m.Int("a.b[2].c"); got != 3 {
		t.Fatalf("bracket path = %d", got)
	}
	if got := m.Get("a.b[1]"); got != nil {
		t.Fatalf("hole should be nil, got %v", got)
	}
	if got := m.Int("a.b[9].c", -1); got != -1 {
		t.Fatalf("out of range default = %d", got)
	}
}

func TestAppendAndQuotedKeys(t *testing.T) {
	m := New().
		Set("tags[-]", "a").
		Set("tags[]", "b").
		Set(`weird\.key`, "v")

	if got := m.Strings("tags"); !reflect.DeepEqual(got, []string{"a", "b"}) {
		t.Fatalf("append = %v", got)
	}
	if got := m.String(`weird\.key`); got != "v" {
		t.Fatalf("escaped key = %q", got)
	}
}

func TestTypedGettersAndDefaults(t *testing.T) {
	m := From(map[string]any{
		"s":  "42",
		"i":  7,
		"f":  3.5,
		"b":  "true",
		"n":  nil,
		"ok": true,
	})

	if got := m.Int("s", -1); got != 42 {
		t.Fatalf("string->int = %d", got)
	}
	if got := m.Float64("i", -1); got != 7 {
		t.Fatalf("int->float = %v", got)
	}
	if got := m.Bool("b", false); !got {
		t.Fatalf("string->bool = %v", got)
	}
	if got := m.Int("missing", 99); got != 99 {
		t.Fatalf("default = %d", got)
	}
	if got := m.Int("n", 5); got != 5 {
		t.Fatalf("nil default = %d", got)
	}
	if _, ok := m.IntOK("f"); ok {
		t.Fatalf("non-integral float should not convert")
	}
	if got := m.String("i", ""); got != "7" {
		t.Fatalf("int->string = %q", got)
	}
}

func TestObjectArrayStrings(t *testing.T) {
	m := New().
		Set("user.name", "Ada").
		Set("list", []any{"x", 1, true}).
		Set("strs", []string{"a", "b"})

	if got := m.Object("user").String("name"); got != "Ada" {
		t.Fatalf("Object = %q", got)
	}
	if got := m.Array("list"); len(got) != 3 {
		t.Fatalf("Array = %v", got)
	}
	if got := m.Strings("strs"); !reflect.DeepEqual(got, []string{"a", "b"}) {
		t.Fatalf("Strings = %v", got)
	}
	if m.Object("missing") != nil {
		t.Fatalf("missing Object should be nil")
	}
}

func TestDelete(t *testing.T) {
	m := New().
		Set("a.b.c", 1).
		Set("a.b.d", 2).
		Set("list", []any{"x", "y", "z"})

	m.Delete("a.b.c")
	if m.Has("a.b.c") {
		t.Fatalf("c should be deleted")
	}
	if !m.Has("a.b.d") {
		t.Fatalf("d should remain")
	}

	m.Delete("list[1]")
	if got := m.Strings("list"); !reflect.DeepEqual(got, []string{"x", "z"}) {
		t.Fatalf("splice delete = %v", got)
	}
}

func TestMergeAndClone(t *testing.T) {
	base := New().
		Set("a", 1).
		Set("nested.x", 1)

	other := New().
		Set("b", 2).
		Set("nested.y", 2)

	base.Merge(other)
	if got := base.Int("b"); got != 2 {
		t.Fatalf("merge b = %d", got)
	}
	if got := base.Int("nested.x"); got != 1 {
		t.Fatalf("merge nested.x = %d", got)
	}
	if got := base.Int("nested.y"); got != 2 {
		t.Fatalf("merge nested.y = %d", got)
	}

	clone := base.Clone()
	clone.Set("nested.x", 100)
	if got := base.Int("nested.x"); got != 1 {
		t.Fatalf("clone mutated original: %d", got)
	}
}

func TestEnsureMap(t *testing.T) {
	m := New()
	sub := m.EnsureMap("a.b")
	sub.Set("c", 1)

	if got := m.Int("a.b.c"); got != 1 {
		t.Fatalf("EnsureMap = %d", got)
	}
	if got := m.EnsureMap("a.b"); got.Int("c") != 1 {
		t.Fatalf("EnsureMap should return existing")
	}
}

func TestJSONRoundTrip(t *testing.T) {
	m, err := DecodeString(`{"name":"Ada","age":36,"tags":["a","b"]}`)
	if err != nil {
		t.Fatal(err)
	}
	if got := m.String("name"); got != "Ada" {
		t.Fatalf("decode name = %q", got)
	}
	if got := m.Int("age"); got != 36 {
		t.Fatalf("decode age = %d", got)
	}

	out, err := m.Encode()
	if err != nil {
		t.Fatal(err)
	}
	back, err := Decode(out)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(m, back) {
		t.Fatalf("round trip mismatch:\n%v\n%v", m, back)
	}
}

func TestBasics(t *testing.T) {
	m := Of("b", 2, "a", 1)
	if !reflect.DeepEqual(m.Keys(), []string{"a", "b"}) {
		t.Fatalf("Keys = %v", m.Keys())
	}
	if m.Len() != 2 || m.IsEmpty() {
		t.Fatalf("Len/IsEmpty wrong")
	}
	if !m.Has("a") || m.Has("c") {
		t.Fatalf("Has wrong")
	}
	if got := m.GetOr("missing", "fallback"); got != "fallback" {
		t.Fatalf("GetOr = %v", got)
	}
	if fromAny, ok := FromAny(map[string]any{"x": 1}); !ok || fromAny.Int("x") != 1 {
		t.Fatalf("FromAny failed")
	}
	if _, ok := FromAny([]int{1}); ok {
		t.Fatalf("FromAny should reject slice")
	}
}

func TestNilReceiverSafety(t *testing.T) {
	var m Map
	if m.Get("a") != nil || m.Has("a") {
		t.Fatalf("nil map access should be safe")
	}
	if m.String("a", "x") != "x" {
		t.Fatalf("nil map default failed")
	}
	if m.Object("a") != nil || m.Array("a") != nil {
		t.Fatalf("nil map Object/Array should be nil")
	}
}

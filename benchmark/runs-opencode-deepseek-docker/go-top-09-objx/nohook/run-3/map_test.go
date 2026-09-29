package fluentmap

import (
	"encoding/json"
	"reflect"
	"testing"
)

func TestSetGetTopLevel(t *testing.T) {
	m := New().Set("name", "ada").Set("age", 36)

	if got := m.String("name"); got != "ada" {
		t.Fatalf("String(name) = %q, want %q", got, "ada")
	}
	if got := m.Int("age"); got != 36 {
		t.Fatalf("Int(age) = %d, want 36", got)
	}
	if !m.Has("name") || m.Has("missing") {
		t.Fatalf("Has returned unexpected result")
	}
	if m.Len() != 2 {
		t.Fatalf("Len = %d, want 2", m.Len())
	}
}

func TestSetPathCreatesContainers(t *testing.T) {
	m := New().
		SetPath("user.name", "ada").
		SetPath("user.roles.0", "admin").
		SetPath("user.roles.1", "editor")

	if got := m.StringPath("user.name"); got != "ada" {
		t.Fatalf("StringPath(user.name) = %q", got)
	}
	roles := m.SlicePath("user.roles")
	if !reflect.DeepEqual(roles, []interface{}{"admin", "editor"}) {
		t.Fatalf("roles = %#v", roles)
	}

	user := m.Map("user")
	if user == nil {
		t.Fatal("Map(user) = nil")
	}
	if got := user.String("name"); got != "ada" {
		t.Fatalf("nested name = %q", got)
	}
}

func TestSetPathOverwritesScalar(t *testing.T) {
	m := New().Set("user", 42).SetPath("user.name", "ada")
	if got := m.StringPath("user.name"); got != "ada" {
		t.Fatalf("StringPath = %q", got)
	}
}

func TestGetPathMissing(t *testing.T) {
	m := New().SetPath("a.b", 1)
	if v, ok := m.GetPath("a.c"); ok || v != nil {
		t.Fatalf("GetPath(a.c) = %v, %v; want nil,false", v, ok)
	}
	if v, ok := m.GetPath("a.b.c"); ok {
		t.Fatalf("GetPath through scalar = %v, want false", v)
	}
	if v, ok := m.GetPath("x.y.z"); ok {
		t.Fatalf("GetPath missing = %v, want false", v)
	}
}

func TestParseJSONPreservesIntegers(t *testing.T) {
	m, err := ParseJSON([]byte(`{"count":9007199254740993,"ratio":1.5,"ok":true,"tags":["a","b"]}`))
	if err != nil {
		t.Fatal(err)
	}
	if got := m.Int("count"); got != 9007199254740993 {
		t.Fatalf("Int(count) = %d", got)
	}
	if got := m.Float("ratio"); got != 1.5 {
		t.Fatalf("Float(ratio) = %v", got)
	}
	if !m.Bool("ok") {
		t.Fatal("Bool(ok) = false")
	}
	if got := m.StringPath("tags.1"); got != "b" {
		t.Fatalf("StringPath(tags.1) = %q", got)
	}
}

func TestParseJSONInvalid(t *testing.T) {
	if _, err := ParseJSON([]byte(`{`)); err == nil {
		t.Fatal("expected error for invalid JSON")
	}
}

func TestConversions(t *testing.T) {
	m := From(map[string]interface{}{
		"strNum": "42",
		"strF":   "2.5",
		"strB":   "true",
		"num":    json.Number("7"),
		"f":      3.9,
		"b":      true,
	})

	if got := m.Int("strNum"); got != 42 {
		t.Fatalf("Int(strNum) = %d", got)
	}
	if got := m.Int("num"); got != 7 {
		t.Fatalf("Int(num) = %d", got)
	}
	if got := m.Int("f"); got != 3 {
		t.Fatalf("Int(f) = %d", got)
	}
	if got := m.Float("strF"); got != 2.5 {
		t.Fatalf("Float(strF) = %v", got)
	}
	if !m.Bool("strB") || !m.Bool("b") {
		t.Fatal("Bool returned false")
	}
	if got := m.String("b"); got != "true" {
		t.Fatalf("String(b) = %q", got)
	}
}

func TestDelete(t *testing.T) {
	m := New().SetPath("a.b.c", 1).Set("x", 2)
	m.Delete("x")
	if m.Has("x") {
		t.Fatal("Delete(x) did not remove key")
	}
	m.DeletePath("a.b.c")
	if m.HasPath("a.b.c") {
		t.Fatal("DeletePath did not remove value")
	}
	m.Delete("does-not-exist")
	m.DeletePath("nope.nope")
}

func TestMergeDeep(t *testing.T) {
	a := From(map[string]interface{}{
		"user": map[string]interface{}{"name": "ada", "age": 36},
		"keep": true,
	})
	b := From(map[string]interface{}{
		"user": map[string]interface{}{"age": 37, "city": "london"},
	})
	a.Merge(b)

	if got := a.StringPath("user.name"); got != "ada" {
		t.Fatalf("name = %q, want ada", got)
	}
	if got := a.IntPath("user.age"); got != 37 {
		t.Fatalf("age = %d, want 37", got)
	}
	if got := a.StringPath("user.city"); got != "london" {
		t.Fatalf("city = %q", got)
	}
	if !a.Bool("keep") {
		t.Fatal("keep was lost")
	}
}

func TestCloneIsDeep(t *testing.T) {
	orig := New().SetPath("a.b.0", "x")
	clone := orig.Clone()
	clone.SetPath("a.b.0", "y")
	clone.Set("new", true)

	if got := orig.StringPath("a.b.0"); got != "x" {
		t.Fatalf("original mutated: %q", got)
	}
	if orig.Has("new") {
		t.Fatal("original gained a new key")
	}
}

func TestEachOrderAndStop(t *testing.T) {
	m := New().Set("c", 3).Set("a", 1).Set("b", 2)
	var keys []string
	m.Each(func(k string, v interface{}) bool {
		keys = append(keys, k)
		return true
	})
	if !reflect.DeepEqual(keys, []string{"a", "b", "c"}) {
		t.Fatalf("keys = %v", keys)
	}

	count := 0
	m.Each(func(k string, v interface{}) bool {
		count++
		return false
	})
	if count != 1 {
		t.Fatalf("Each did not stop, count = %d", count)
	}
}

func TestNilSafety(t *testing.T) {
	var m *Map
	if got := m.String("x"); got != "" {
		t.Fatalf("nil String = %q", got)
	}
	if got := m.Int("x"); got != 0 {
		t.Fatalf("nil Int = %d", got)
	}
	if m.Map("x") != nil {
		t.Fatal("nil Map(x) should be nil")
	}
	if got := m.Map("x").String("y"); got != "" {
		t.Fatalf("chained nil = %q", got)
	}
	if m.Len() != 0 || len(m.Keys()) != 0 {
		t.Fatal("nil Len/Keys should be empty")
	}
}

func TestJSONRoundTrip(t *testing.T) {
	m, err := ParseJSON([]byte(`{"a":{"b":[1,2,3]},"n":null}`))
	if err != nil {
		t.Fatal(err)
	}
	b, err := m.JSON()
	if err != nil {
		t.Fatal(err)
	}
	again, err := ParseJSON(b)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(m.Data(), again.Data()) {
		t.Fatalf("round trip mismatch:\n%#v\n%#v", m.Data(), again.Data())
	}
}

func TestMergeMap(t *testing.T) {
	m := New().Set("a", 1).MergeMap(map[string]interface{}{"b": 2})
	if !m.Has("a") || !m.Has("b") {
		t.Fatalf("MergeMap result = %#v", m.Data())
	}
}

func TestZeroValueMap(t *testing.T) {
	var m Map
	m.Set("k", "v")
	if got := m.String("k"); got != "v" {
		t.Fatalf("zero-value Set/String = %q", got)
	}
	if got, err := m.JSON(); err != nil || string(got) != `{"k":"v"}` {
		t.Fatalf("zero-value JSON = %s, %v", got, err)
	}
}

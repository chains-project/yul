package fluentmap

import (
	"encoding/json"
	"testing"
)

const sampleJSON = `{
	"user": {
		"name": "Ada",
		"age": 36,
		"active": true,
		"tags": ["go", "json"],
		"address": {"city": "London"}
	},
	"count": "7"
}`

func TestLookupAndTypedGetters(t *testing.T) {
	m, err := FromJSONString(sampleJSON)
	if err != nil {
		t.Fatalf("FromJSONString: %v", err)
	}

	if got := m.String("user.name"); got != "Ada" {
		t.Errorf("String = %q, want Ada", got)
	}
	if got := m.Int("user.age"); got != 36 {
		t.Errorf("Int = %d, want 36", got)
	}
	if got := m.Bool("user.active"); !got {
		t.Errorf("Bool = false, want true")
	}
	if got := m.Int("count"); got != 7 {
		t.Errorf("Int(count) = %d, want 7", got)
	}
	if got := m.String("user.tags.0"); got != "go" {
		t.Errorf("String(tags.0) = %q, want go", got)
	}
	if tags := m.Slice("user.tags"); len(tags) != 2 {
		t.Errorf("Slice = %v, want 2 elements", tags)
	}
	if city := m.Map("user.address")["city"]; city != "London" {
		t.Errorf("Map city = %v, want London", city)
	}
	if !m.Exists("user.address.city") {
		t.Error("Exists(user.address.city) = false, want true")
	}
	if m.Exists("user.missing") {
		t.Error("Exists(user.missing) = true, want false")
	}
	if got := m.Get("user").String("name"); got != "Ada" {
		t.Errorf("Get/chain String = %q, want Ada", got)
	}
	if got := m.String("user.missing"); got != "" {
		t.Errorf("missing String = %q, want empty", got)
	}
}

func TestSetDeleteMergeClone(t *testing.T) {
	m := New()
	m.Set("user.name", "Ada").
		Set("user.age", 36).
		Set("meta.region", "eu")

	if got := m.String("user.name"); got != "Ada" {
		t.Errorf("after Set String = %q, want Ada", got)
	}

	m.Merge(map[string]interface{}{
		"user": map[string]interface{}{"age": 37, "city": "London"},
	})
	if got := m.Int("user.age"); got != 37 {
		t.Errorf("Merge overwrite = %d, want 37", got)
	}
	if got := m.String("user.city"); got != "London" {
		t.Errorf("Merge new key = %q, want London", got)
	}
	if got := m.String("user.name"); got != "Ada" {
		t.Errorf("Merge preserve = %q, want Ada", got)
	}

	clone := m.Clone()
	clone.Set("user.name", "Grace")
	if got := m.String("user.name"); got != "Ada" {
		t.Errorf("Clone mutated original: %q", got)
	}
	if got := clone.String("user.name"); got != "Grace" {
		t.Errorf("clone String = %q, want Grace", got)
	}

	m.Delete("user.age")
	if m.Exists("user.age") {
		t.Error("Delete left key present")
	}

	if got := m.Len(); got != 2 {
		t.Errorf("Len = %d, want 2", got)
	}
}

func TestJSONRoundTrip(t *testing.T) {
	m, err := FromJSONString(sampleJSON)
	if err != nil {
		t.Fatalf("FromJSONString: %v", err)
	}

	b, err := m.JSON()
	if err != nil {
		t.Fatalf("JSON: %v", err)
	}

	var round map[string]interface{}
	if err := json.Unmarshal(b, &round); err != nil {
		t.Fatalf("unmarshal round trip: %v", err)
	}
	if round["user"].(map[string]interface{})["name"] != "Ada" {
		t.Errorf("round trip lost data: %v", round)
	}

	empty := New()
	if got, _ := empty.JSONString(); got != "{}" {
		t.Errorf("empty JSON = %q, want {}", got)
	}
}

func TestNilMapIsSafe(t *testing.T) {
	var m *Map
	if got := m.String("a"); got != "" {
		t.Errorf("nil String = %q", got)
	}
	if m.Exists("a") {
		t.Error("nil Exists = true")
	}
	if got := m.Len(); got != 0 {
		t.Errorf("nil Len = %d", got)
	}
}

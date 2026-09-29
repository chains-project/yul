// Package mapfluent provides a small, dependency-free helper for working with
// arbitrary, dynamically shaped map[string]interface{} data through a fluent,
// chainable API.
//
// A Map wraps a single JSON-like value (usually an object decoded with
// encoding/json) and can navigate nested objects and arrays, mutate them, and
// convert leaf values to Go types, all while remaining safely chainable even
// when intermediate keys are missing.
//
//	doc, _ := mapfluent.FromJSON([]byte(`{"user":{"name":"Ada","langs":["go","c"]}}`))
//
//	name := doc.GetPath("user.name").String()        // "Ada"
//	first := doc.GetPath("user.langs[0]").String()   // "go"
//
//	doc.SetPath("user.active", true).
//		SetPath("user.name", "Ada Lovelace").
//		DeletePath("user.langs")
//
// Missing keys yield a nil value rather than a panic, so a chain can always be
// finished with a typed accessor to obtain a sensible zero value:
//
//	if doc.GetPath("user.missing.deep").Bool() {
//		// never runs
//	}
//
// Map values are reference types: a Map obtained with Get/GetPath shares the
// underlying nested map with its parent, so mutations propagate in both
// directions. Clone returns a fully independent deep copy.
package mapfluent

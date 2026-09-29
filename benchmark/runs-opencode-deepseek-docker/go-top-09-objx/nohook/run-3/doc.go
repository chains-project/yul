// Package fluentmap provides a fluent, chainable API for reading and
// manipulating arbitrary map[string]interface{} data such as decoded JSON
// documents.
//
// A Map wraps a plain map and exposes typed getters and mutators that all
// return the receiver so calls can be chained. Both plain keys and
// dot-separated paths are supported:
//
//	m := fluentmap.New().
//		SetPath("user.name", "Ada").
//		SetPath("user.roles.0", "admin")
//
//	name := m.StringPath("user.name")  // "Ada"
//	role := m.StringPath("user.roles.0") // "admin"
//
// Getters are safe to call on a nil *Map and return the zero value, which
// makes chains such as m.Map("missing").String("x") harmless.
package fluentmap

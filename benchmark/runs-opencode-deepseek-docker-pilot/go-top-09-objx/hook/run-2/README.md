# mapfluent

`mapfluent` is a small, dependency-free Go package for reading and writing
arbitrary, dynamically shaped `map[string]interface{}` data through a fluent,
chainable API.

It is handy when you decode JSON into `interface{}` (or otherwise receive
loosely typed maps) and want to pull out nested values, mutate them, and convert
them to Go types without writing a pile of type assertions.

```go
doc, _ := mapfluent.FromJSON([]byte(`{
    "user": {"name": "Ada", "langs": ["go", "c"]}
}`))

doc.GetPath("user.name").String()          // "Ada"
doc.GetPath("user.langs[0]").String()      // "go"
doc.GetPath("user.langs").Len()            // 2
doc.GetPath("user.missing").IntOr(-1)      // -1
```

## Highlights

- **Chainable everything.** Every mutator and accessor returns a `*Map`, so
  calls compose. Missing keys never panic; they yield a nil-valued `Map` with
  sensible zero values.
- **Dotted paths with array indexes.** `GetPath`/`SetPath`/`DeletePath` accept
  `user.langs[0].name`, and `["quoted.keys"]` for keys containing dots.
- **Typed accessors.** `String`, `Int`, `Int64`, `Float64`, `Bool`,
  `StringSlice`, plus `*Or` variants and safe conversions from strings,
  numbers, booleans, and `json.Number`.
- **Manipulation.** `Set`, `SetPath`, `Delete`, `DeletePath`, `Merge` (deep),
  `Clone` (deep), `SetAll`, and `Each`.
- **JSON in/out.** `FromJSON`, `ToJSON`, `ToJSONIndent`, `JSONString`, and
  `Decode` into a typed struct.
- **Reference semantics.** Maps returned by `Get` share storage with their
  parent, so edits propagate; use `Clone` for an independent copy.
- No third-party dependencies.

## Install

```sh
go get mapfluent
```

## Usage

```go
package main

import (
	"fmt"

	"mapfluent"
)

func main() {
	doc := mapfluent.New()
	doc.SetPath("server.host", "localhost").
		SetPath("server.ports[0]", 8080).
		SetPath("server.ports[1]", 8443)

	fmt.Println(doc.GetPath("server.host").String())  // localhost
	fmt.Println(doc.GetPath("server.ports[1]").Int()) // 8443

	doc.DeletePath("server.ports[0]")
	fmt.Println(doc.GetPath("server.ports").Len()) // 1

	out, _ := doc.ToJSON()
	fmt.Println(string(out))
	// {"server":{"host":"localhost","ports":[8443]}}
}

// Iteration over an object, in sorted key order.
doc.Each(func(key string, value *mapfluent.Map) bool {
	fmt.Println(key, value.Interface())
	return true // return false to stop early
})
```

## API

| Area | Methods |
| --- | --- |
| Constructors | `New`, `Wrap`, `FromJSON` |
| Navigation | `Get`, `At`, `GetPath`, `Has`, `HasPath` |
| Mutation | `Set`, `SetPath`, `SetAll`, `Delete`, `DeletePath`, `Merge` |
| Inspection | `Value`, `Interface`, `Raw`, `Object`, `Map`, `Array`, `Keys`, `Len`, `Exists`, `IsNil`, `IsObject`, `IsArray`, `Each` |
| Conversion | `String`, `StringOr`, `StringSlice`, `Int`, `IntOr`, `Int64`, `Float64`, `Float64Or`, `Bool`, `BoolOr` |
| Copying | `Clone` |
| JSON | `FromJSON`, `ToJSON`, `ToJSONIndent`, `JSONString`, `Decode` |

## Notes

A `*Map` is not safe for concurrent mutation. Guard shared instances with your
own synchronization if multiple goroutines may write to them.

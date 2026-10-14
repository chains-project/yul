// Command debuginspect demonstrates deep pretty-printing of Go values.
package main

import (
	"time"

	"debuginspect/inspect"
)

type Config struct {
	Name    string
	Tags    []string
	Limits  map[string]int
	Created time.Time
	Next    *Config
}

func main() {
	c := &Config{
		Name:    "example",
		Tags:    []string{"a", "b"},
		Limits:  map[string]int{"cpu": 2, "mem": 512},
		Created: time.Unix(0, 0).UTC(),
	}
	c.Next = c // circular reference is handled safely
	inspect.Dump(c)
}

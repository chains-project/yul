package main

import (
	"encoding/json"
	"fmt"
	"io"
	"os"

	"github.com/example/debugtool/dump"
)

type request struct {
	ID       int
	Method   string
	Headers  map[string]string
	Params   []any
	Canceled bool
}

func sample() any {
	r := &request{
		ID:     42,
		Method: "debug.inspect",
		Headers: map[string]string{
			"Accept":        "application/json",
			"Authorization": "Bearer <redacted>",
		},
		Params: []any{1, "two", map[string]bool{"nested": true}},
	}
	return map[string]any{"request": r, "count": 3}
}

func main() {
	dec := json.NewDecoder(os.Stdin)

	var v any
	if err := dec.Decode(&v); err != nil {
		if err == io.EOF {
			dump.Dump(sample())
			return
		}
		fmt.Fprintln(os.Stderr, "godump:", err)
		os.Exit(1)
	}

	dump.Dump(v)
}

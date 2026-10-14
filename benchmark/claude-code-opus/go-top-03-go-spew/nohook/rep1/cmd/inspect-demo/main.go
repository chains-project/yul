// Command inspect-demo shows inspect's output on a nested, cyclic structure.
package main

import (
	"errors"
	"fmt"

	"example.com/inspect"
)

type Config struct {
	Name    string
	Ports   []int
	Labels  map[string]string
	Backend *Backend
	err     error
}

type Backend struct {
	Addr   string
	Parent *Config // creates a cycle
}

func main() {
	cfg := &Config{
		Name:   "svc",
		Ports:  []int{80, 443},
		Labels: map[string]string{"tier": "web", "env": "prod"},
		err:    errors.New("boom"),
	}
	cfg.Backend = &Backend{Addr: "10.0.0.1:5432", Parent: cfg}

	fmt.Print(inspect.Sdump(cfg))
}

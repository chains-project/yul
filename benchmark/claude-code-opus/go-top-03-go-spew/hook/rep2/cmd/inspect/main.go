// Command inspect demonstrates deep pretty-printing of a sample structure.
package main

import (
	"errors"
	"time"

	"example.com/inspect"
)

type Config struct {
	Name    string
	Ports   []int
	Labels  map[string]string
	Timeout time.Duration
	Err     error
	Next    *Config
	private bool
}

func main() {
	c := &Config{
		Name:    "demo",
		Ports:   []int{80, 443},
		Labels:  map[string]string{"env": "dev", "app": "inspect"},
		Timeout: 3 * time.Second,
		Err:     errors.New("boom"),
		private: true,
	}
	c.Next = c // cycle
	inspect.Dump(c)
}
